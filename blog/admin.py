from django.contrib import admin
from .models import Post, Comment
from django.utils.html import format_html

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "created_at", "thumb")
    

    def thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:80px;height:auto;object-fit:cover;border-radius:4px;" />', obj.image.url)
        return "-"
    thumb.short_description = "Image"
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post','author','created_at')
