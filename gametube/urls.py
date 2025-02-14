from django.urls import path
from . import views

app_name = 'gametube'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('liked-videos/', views.liked_videos, name='liked_videos'),
    path('register/', views.register_view, name='register'),
    path('upload/', views.upload_video, name='upload'),
    path('video/<int:video_id>/', views.video_detail, name='video_detail'),
    path('user/<str:username>/', views.user_profile, name='user_profile'),
    path('subscribe/<str:username>/', views.subscribe, name='subscribe'),
    path('subscriptions/', views.subscriptions, name='subscriptions'),
    path('watch-history/', views.watch_history, name='watch_history'),
    path('game-downloads/', views.game_downloads, name='game_downloads'),
    path('device-purchases/', views.device_purchases, name='device_purchases'),
    path('game-boards/', views.game_boards, name='game_boards'),
]