from django.conf import settings
from django.conf.urls import url
from django.urls import path
from django.views.static import serve

from . import views

urlpatterns = [
    path('',
         views.index,
         name='index'),
    path('new/',
         views.new_post,
         name='new_post'),
    path('group/<slug:slug>/',
         views.group_posts,
         name='group'),
    path('follow/',
         views.follow_index,
         name='follow_index'),
    path('<str:username>/',
         views.profile,
         name='profile'),
    path('<str:username>/<int:post_id>/',
         views.post_view,
         name='post'),
    path('<str:username>/<int:post_id>/edit/',
         views.post_edit,
         name='post_edit'),
    path("<username>/<int:post_id>/comment",
         views.add_comment,
         name="add_comment"),
    path("<str:username>/follow/",
         views.profile_follow,
         name="profile_follow"),
    path("<str:username>/unfollow/",
         views.profile_unfollow,
         name="profile_unfollow"),
    path('500/',
         views.server_error,
         name='500'),
    path('404/',
         views.page_not_found,
         name='404'),
]

if not settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve,
            {'document_root': settings.MEDIA_ROOT}),
        url(r'^static/(?P<path>.*)$', serve,
            {'document_root': settings.STATIC_ROOT}),
    ]
