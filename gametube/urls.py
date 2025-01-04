
from django.urls import path
from . import views

app_name = 'gametube'

urlpatterns = [
    path('', views.home, name='home'),
    path('video/<int:video_id>/', views.video_detail, name='video_detail'),
    path('upload/', views.upload_video, name='upload_video'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('video/<int:video_id>/like/', views.like_video, name='like_video'),
    path('user/<str:username>/', views.user_profile, name='user_profile'),
    path('subscribe/<str:username>/', views.subscribe, name='subscribe'),
    path('subscriptions/', views.subscriptions, name='subscriptions'),
    path('downloads/', views.game_downloads, name='game_downloads'),
    path('devices/', views.device_purchases, name='device_purchases'),
    path('boards/', views.game_boards, name='game_boards'),
    path('board/<int:board_id>/', views.board_detail, name='board_detail'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('liked-videos/', views.liked_videos, name='liked_videos'),
    path('watch-history/', views.watch_history, name='watch_history'),
    path('comment/<int:comment_id>/reply/', views.reply_comment, name='reply_comment'),
    path('comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
]
