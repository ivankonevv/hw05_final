from django.contrib import admin

from .models import Post, Group, Comment, Follow


class GroupAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("pk",
                    "title",
                    "slug",
                    "description",
                    )
    search_fields = ("title",)
    list_filter = ("title",)
    empty_value_display = "-пусто-"


class PostAdmin(admin.ModelAdmin):
    list_display = ("pk",
                    "text",
                    "pub_date",
                    "author",
                    "group",
                    )
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', )
    list_filter = ('created', )
    search_fields = ('text',)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'user')
    list_filter = ('author', 'user')


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)

