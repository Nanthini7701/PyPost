# blog/models.py
from django.db import models
from django.conf import settings
from django.urls import reverse, NoReverseMatch
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver

User = settings.AUTH_USER_MODEL


class Post(models.Model):
    title = models.CharField(max_length=255)
    # allow null/blank so old rows won't break (you can migrate / backfill later)
    slug = models.SlugField(max_length=255, unique=True, null=False, blank=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to="posts/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="liked_posts", blank=True)
    # NOTE: if your DB already had a likes ManyToManyField, uncomment the following line
    # likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="liked_posts", blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # auto-generate a slug if missing
        if not self.slug:
            base = slugify(self.title) or "post"
            slug_candidate = base
            i = 1
            # ensure uniqueness
            while Post.objects.filter(slug=slug_candidate).exists():
                slug_candidate = f"{base}-{i}"
                i += 1
            self.slug = slug_candidate
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """
        Prefer slug URL (namespaced). If slug is missing, fallback to pk-based detail.
        This avoids returning 'None' for missing slugs.
        """
        if self.slug:
            try:
                return reverse("blog:post_detail", kwargs={"slug": self.slug})
            except NoReverseMatch:
                # fall through to pk-based fallback below
                pass
        # fallback
        try:
            return reverse("blog:post_detail_pk", kwargs={"pk": self.pk})
        except NoReverseMatch:
            return "/"

    @classmethod
    def trending_posts(cls, by="likes", limit=5):
        """
        Returns a queryset of trending posts.
        - If you have a 'likes' ManyToManyField on Post, this will use it.
        - Otherwise it falls back to ordering by number of comments.
        """
        from django.db.models import Count

        if "likes" in [f.name for f in cls._meta.get_fields()]:
            return cls.objects.annotate(num_likes=Count("likes")).order_by("-num_likes")[:limit]
        # fallback: use comments count
        if "comments" in [f.name for f in cls._meta.get_fields()]:
            return cls.objects.annotate(num_comments=Count("comments")).order_by("-num_comments")[:limit]
        return cls.objects.order_by("-created_at")[:limit]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="profiles/", null=True, blank=True)
    bio = models.TextField(null=True, blank=True)

    def __str__(self):
        # avoid accessing username if custom user model doesn't have it
        username = getattr(self.user, "username", str(self.user))
        return f"Profile({username})"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_profile(sender, instance, created, **kwargs):
    # ensure a Profile instance exists for every user
    if created:
        Profile.objects.create(user=instance)
    else:
        Profile.objects.get_or_create(user=instance)
