from django.urls import path, re_path 

from . import views


app_name = 'notifications'

urlpatterns = [
    re_path(r'^$', views.AllNotificationsList.as_view(), name='all'),
    re_path(r'^unread/$', views.UnreadNotificationsList.as_view(), name='unread'),
    re_path(r'^mark-all-as-read/$', views.mark_all_as_read, name='mark_all_as_read'),
    path(
        'mark-category-as-read/<category>/', 
        views.mark_category_as_read, 
        name='mark_category_as_read'
    ),
    path(
        'delete-category-notifs/<category>/', 
        views.delete_category_notifs, 
        name='delete_category_notifs'
    ),
    path(
        'mark-post-as-read/<str:category>-<int:obj_id>-<str:app_name>-<str:model_name>/', 
        views.mark_post_notifs_as_read, 
        name='mark_post_as_read'
    ),
    path(
        'delete-post-notifs/<str:category>-<int:obj_id>-<str:app_name>-<str:model_name>/', 
        views.delete_post_notifs, 
        name='delete_post_notifs'
    ),
    path(
        'mark-post-as-read/<str:category>/', 
        views.mark_all_post_notifs_as_read, 
        name='mark_all_posts_as_read'
    ),
    path(
        'delete-post-notifs/<str:category>/', 
        views.delete_all_post_notifs, 
        name='delete_all_post_notifs'
    ),
    re_path(r'^mark-as-read/(?P<id>\d+)/$', views.mark_as_read, name='mark_as_read'),
    re_path(r'^mark-as-unread/(?P<id>\d+)/$', views.mark_as_unread, name='mark_as_unread'),
    re_path(r'^delete/(?P<id>\d+)/$', views.delete, name='delete'),
    re_path(r'^api/unread_count/$', views.live_unread_notification_count, name='live_unread_notification_count'),
    re_path(r'^api/all_count/$', views.live_all_notification_count, name='live_all_notification_count'),
    re_path(r'^api/unread_list/$', views.live_unread_notification_list, name='live_unread_notification_list'),
    re_path(r'^api/all_list/', views.live_all_notification_list, name='live_all_notification_list'),
]

