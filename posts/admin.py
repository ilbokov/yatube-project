from django.contrib import admin

from .models import Comment, Follow, Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Класс для вывода объектов класса Post в админке."""
    list_display = ("pk", "text", "pub_date", "author", "group")
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """Класс для вывода объектов класса Group в админке."""
    list_display = ("title", "slug")
    search_fields = ("title",)
    empty_value_display = "-пусто-"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Класс для вывода объектов класса Comment в админке."""
    list_display = ("pk", "text", "author", "post")
    search_fields = ("text",)
    empty_value_display = "-пусто-"


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Класс для вывода объектов класса Follow в админке."""
    list_display = ("user", "author")
    search_fields = ("user",)
    empty_value_display = "-пусто-"
