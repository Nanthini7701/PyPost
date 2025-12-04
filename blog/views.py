# blog/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import get_user_model
from django.views.generic import DetailView

from .forms import UserForm, ProfileForm, PostForm, CommentForm, RegisterForm
from .models import Post, Comment, Profile

User = get_user_model()


def home(request):
    # latest posts for main area
    posts = Post.objects.order_by("-created_at")[:12]

    # trending posts: uses Post.trending_posts() which falls back safely
    trending = Post.trending_posts(limit=6)

    return render(request, "home.html", {"posts": posts, "trending": trending})


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("blog:post_list")
    else:
        form = RegisterForm()
    return render(request, "blog/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            return redirect("blog:post_list")
        else:
            messages.error(request, "Invalid credentials.")
    return render(request, "blog/login.html")


def logout_view(request):
    auth_logout(request)
    # send to posts list (namespaced)
    return redirect("blog:post_list")


@login_required
def profile(request):
    user = request.user
    profile = getattr(user, "profile", None)
    posts = Post.objects.filter(author=user).order_by("-created_at")
    return render(request, "blog/profile.html", {"user_obj": user, "profile": profile, "posts": posts})


@login_required
def settings_view(request):
    user = request.user
    profile = getattr(user, "profile", None)

    if request.method == "POST":
        uform = UserForm(request.POST, instance=user)
        # ProfileForm is a ModelForm that expects instance if profile exists
        pform = ProfileForm(request.POST, request.FILES, instance=profile) if profile is not None else ProfileForm(request.POST, request.FILES)
        if "update_profile" in request.POST:
            if uform.is_valid() and (pform.is_valid() if isinstance(pform, ProfileForm.__class__) else True):
                uform.save()
                if profile is not None and isinstance(pform, type(ProfileForm())):
                    pform.save()
                messages.success(request, "Profile updated successfully.")
                return redirect("blog:profile")
            else:
                messages.error(request, "Please correct the errors below.")
        elif "change_password" in request.POST:
            pwd_form = PasswordChangeForm(user, request.POST)
            if pwd_form.is_valid():
                user = pwd_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password changed successfully.")
                return redirect("blog:profile")
            else:
                messages.error(request, "Please fix the password errors.")
    else:
        uform = UserForm(instance=user)
        pform = ProfileForm(instance=profile) if profile is not None else ProfileForm()
        pwd_form = PasswordChangeForm(user)

    return render(request, "blog/settings.html", {"uform": uform, "pform": pform, "pwd_form": pwd_form, "profile": profile})


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Post created.")
            return redirect(post.get_absolute_url())
    else:
        form = PostForm()
    return render(request, "blog/post_form.html", {"form": form, "action": "Create"})


@login_required
def post_update(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.error(request, "You cannot edit this post.")
        return redirect(post.get_absolute_url())
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated.")
            return redirect(post.get_absolute_url())
    else:
        form = PostForm(instance=post)
    return render(request, "blog/post_form.html", {"form": form, "action": "Edit"})


@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.error(request, "You cannot delete this post.")
        return redirect(post.get_absolute_url())
    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted.")
        return redirect("blog:post_list")
    return render(request, "blog/post_confirm_delete.html", {"post": post})


@login_required
def post_like(request, pk):
    """
    This view toggles a like. It expects Post to have a ManyToMany 'likes' field.
    If your Post model does not have likes, this view will raise; see note below.
    """
    post = get_object_or_404(Post, pk=pk)
    user = request.user

    # safe-check: only run if 'likes' exists on Post instance
    if hasattr(post, "likes"):
        if user in post.likes.all():
            post.likes.remove(user)
        else:
            post.likes.add(user)
    else:
        messages.error(request, "Like feature is not configured on Post model.")
    return redirect(post.get_absolute_url())


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, "Comment added.")
    return redirect(post.get_absolute_url())


def post_detail(request, slug=None):
    """
    Handle slug detail; if slug is None or 'None', try pk-based fallback or redirect.
    """
    # Defensive: if someone requests 'None' or empty by mistake, try safe fallback
    if not slug or slug == "None":
        # try to find a post with empty slug (very rare) or redirect to posts list
        # Option A: redirect to posts list
        return redirect("blog:post_list")

    post = get_object_or_404(Post, slug=slug)
    return render(request, "blog/post_detail.html", {"post": post})

def post_list(request):
    posts = Post.objects.all().order_by("-created_at")
    return render(request, "blog/post_list.html", {"posts": posts})


# Optional class-based view example (if you prefer to use these in urls)
class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"
