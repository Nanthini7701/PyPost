# blog/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "blog"

urlpatterns = [
    # home & listing
    path("", views.home, name="home"),
    path("posts/", views.post_list, name="post_list"),
    path("posts/new/", views.post_create, name="post_create"),

    # detail routes (slug preferred)
    path("posts/<slug:slug>/", views.post_detail, name="post_detail"),
    # pk-based fallback detail (different name to avoid collision)
    path("posts/id/<int:pk>/", views.PostDetailView.as_view(), name="post_detail_pk"),

    # post actions
    path("posts/<int:pk>/edit/", views.post_update, name="post_update"),
    path("posts/<int:pk>/delete/", views.post_delete, name="post_delete"),
    path("posts/<int:pk>/like/", views.post_like, name="post_like"),
    path("posts/<int:pk>/comment/", views.add_comment, name="add_comment"),

    # auth
    path("accounts/register/", views.register_view, name="register"),
    path("accounts/login/", views.login_view, name="login"),
    path("accounts/logout/", views.logout_view, name="logout"),
    # optional logout redirect
    path("logout/", auth_views.LogoutView.as_view(next_page="/accounts/register/"), name="logout_redirect"),
    # profile / settings
    path("profile/", views.profile, name="profile"),
    path("settings/", views.settings_view, name="settings"),

    # optional: built-in password reset views if you add templates
    path(
        "accounts/password_reset/",
        auth_views.PasswordResetView.as_view(template_name="registration/password_reset_form.html"),
        name="password_reset",
    ),
    path(
        "accounts/password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "accounts/reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"),
        name="password_reset_confirm",
    ),
    path(
        "accounts/reset/done/",
        auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"),
        name="password_reset_complete",
    ),
]
