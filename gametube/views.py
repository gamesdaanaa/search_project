from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.core.cache import cache
from django.http import HttpResponseForbidden
from functools import wraps
import time

def rate_limit(key_prefix, limit=5, period=60):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            key = f"{key_prefix}:{request.user.id}"
            count = cache.get(key, 0)
            
            if count >= limit:
                return HttpResponseForbidden('レートリミットを超えました。しばらく待ってから再試行してください。')
            
            cache.set(key, count + 1, period)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
from django.contrib.auth.models import User
from .models import Video, UserProfile, Comment, Subscription, Like
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver
from .models import Video, GameBoard, GameDownload, DevicePurchase, WatchHistory

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 900  # 15 minutes (seconds)

@receiver(user_login_failed)
def handle_login_failed(sender, credentials, request, **kwargs):
    username = credentials.get('username', '')
    ip_address = request.META.get('REMOTE_ADDR', '')
    attempts_key = f'login_attempts_{ip_address}_{username}'
    attempts = cache.get(attempts_key, 0) + 1
    cache.set(attempts_key, attempts, LOCKOUT_TIME)


@login_required
def like_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    like, created = Like.objects.get_or_create(user=request.user, video=video)

    if not created:
        like.delete()
        return JsonResponse({'status': 'unliked'})

    return JsonResponse({'status': 'liked'})


import jwt
from django.conf import settings
from django_otp import devices_for_user
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.core.exceptions import ValidationError

def generate_jwt_token(user):
    payload = {
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + settings.JWT_EXPIRATION_DELTA
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def verify_2fa(user, otp_code):
    devices = devices_for_user(user)
    for device in devices:
        if device.verify_token(otp_code):
            return True
    return False

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        otp_code = request.POST.get('otp_code')
        
        
        ip_address = request.META.get('REMOTE_ADDR', '')
        attempts_key = f'login_attempts_{ip_address}_{username}'
        attempts = cache.get(attempts_key, 0)

        if attempts >= MAX_LOGIN_ATTEMPTS:
            messages.error(request, 'アカウントが一時的にロックされています。15分後に再試行してください。')
            return render(request, 'gametube/login.html')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            cache.delete(attempts_key)
            return redirect('gametube:home')
        else:
            cache.set(attempts_key, attempts + 1, LOCKOUT_TIME)
            messages.error(request, 'ユーザー名またはパスワードが無効です')
    return render(request, 'gametube/login.html')

def logout_view(request):
    logout(request)
    return redirect('gametube:home')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'gametube/register.html')

        user = User.objects.create_user(username=username, password=password, email=email)
        login(request, user)
        return redirect('gametube:home')
    return render(request, 'gametube/register.html')

import magic
import hashlib
from django.core.exceptions import ValidationError

def validate_file_size(file):
    max_size = 500 * 1024 * 1024  # 500MB
    if file.size > max_size:
        raise ValidationError('ファイルサイズは500MB以下にしてください。')

def validate_file_type(file):
    mime = magic.Magic()
    file_type = mime.from_buffer(file.read(1024))
    file.seek(0)
    
    allowed_types = {
        'video': ['video/mp4', 'video/webm'],
        'image': ['image/jpeg', 'image/png']
    }
    
    if 'video' in file_type.lower() and file.content_type not in allowed_types['video']:
        raise ValidationError('無効な動画形式です。')
    elif 'image' in file_type.lower() and file.content_type not in allowed_types['image']:
        raise ValidationError('無効な画像形式です。')

@login_required
def upload_video(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        video_file = request.FILES.get('video')
        thumbnail = request.FILES.get('thumbnail')
        
        try:
            if video_file:
                validate_file_size(video_file)
                validate_file_type(video_file)
            if thumbnail:
                validate_file_size(thumbnail)
                validate_file_type(thumbnail)
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect('gametube:upload')
            
        category = request.POST.get('category')
        age_restriction = request.POST.get('age_restriction')

        # ファイル形式チェック
        allowed_video_types = ['video/mp4', 'video/webm', 'video/ogg']
        allowed_image_types = ['image/jpeg', 'image/png', 'image/gif']
        max_file_size = 500 * 1024 * 1024  # 500MB

        if video_file:
            if video_file.content_type not in allowed_video_types:
                messages.error(request, '許可されていない動画形式です')
                return redirect('gametube:upload')
            if video_file.size > max_file_size:
                messages.error(request, 'ファイルサイズが大きすぎます')
                return redirect('gametube:upload')

        if thumbnail:
            if thumbnail.content_type not in allowed_image_types:
                messages.error(request, '許可されていない画像形式です')
                return redirect('gametube:upload')

        if title and video_file and thumbnail:
            video = Video.objects.create(
                title=title,
                description=description,
                video_file=video_file,
                thumbnail=thumbnail,
                uploader=request.user,
                category=category,
                age_restriction=age_restriction
            )
            return redirect('gametube:video_detail', video_id=video.id)

    return render(request, 'gametube/upload.html')

def home(request):
    videos = Video.objects.all().order_by('-created_at')
    return render(request, 'gametube/home.html', {'videos': videos})

def video_detail(request, video_id):
    video = get_object_or_404(Video, pk=video_id)
    comments = Comment.objects.filter(video=video, parent=None).order_by('-created_at')
    if request.user.is_authenticated:
        like = Like.objects.filter(user=request.user, video=video).first()
    else:
        like = None

    context = {
        'video': video,
        'comments': comments,
        'like': like
    }
    return render(request, 'gametube/video_detail.html', context)

def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    videos = Video.objects.filter(uploader=user).order_by('-created_at')

    is_subscribed = False
    if request.user.is_authenticated:
        is_subscribed = Subscription.objects.filter(subscriber=request.user, channel=user).exists()

    context = {
        'profile_user': user,
        'videos': videos,
        'is_subscribed': is_subscribed,
        'subscribers_count': Subscription.objects.filter(channel=user).count(),
    }
    return render(request, 'gametube/user_profile.html', context)

@login_required
def subscribe(request, username):
    channel = get_object_or_404(User, username=username)
    subscription, created = Subscription.objects.get_or_create(
        subscriber=request.user,
        channel=channel
    )

    if not created:
        subscription.delete()
        subscribed = False
    else:
        subscribed = True

    subscribers_count = Subscription.objects.filter(channel=channel).count()

    return JsonResponse({
        'subscribed': subscribed,
        'subscribers_count': subscribers_count
    })

@login_required
def subscriptions(request):
    user_subscriptions = Subscription.objects.filter(subscriber=request.user)
    videos = Video.objects.filter(uploader__in=[sub.channel for sub in user_subscriptions]).order_by('-created_at')
    return render(request, 'gametube/subscriptions.html', {'videos': videos})

@login_required
def game_downloads(request):
    downloads = GameDownload.objects.all().order_by('-created_at')
    return render(request, 'gametube/game_downloads.html', {'downloads': downloads})

@login_required
def device_purchases(request):
    devices = DevicePurchase.objects.all().order_by('-created_at')
    return render(request, 'gametube/device_purchases.html', {'devices': devices})

@login_required
def game_boards(request):
    boards = GameBoard.objects.all().order_by('-created_at')
    return render(request, 'gametube/game_boards.html', {'boards': boards})

@login_required
def board_detail(request, board_id):
    board = get_object_or_404(GameBoard, id=board_id)
    messages = ChatMessage.objects.filter(board=board).order_by('-created_at')
    return render(request, 'gametube/game_board.html', {'board': board, 'messages': messages})

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})

@login_required
def liked_videos(request):
    likes = Like.objects.filter(user=request.user).order_by('-created_at')
    videos = [like.video for like in likes]
    return render(request, 'gametube/liked_videos.html', {'videos': videos})

@login_required
def watch_history(request):
    history = WatchHistory.objects.filter(user=request.user).order_by('-watched_at')
    return render(request, 'gametube/watch_history.html', {'history': history})

from django.utils.html import escape

from django.core.cache import cache
from django.core.exceptions import ValidationError
import re

def check_spam(content):
    spam_patterns = [
        r'https?://',
        r'www\.',
        r'buy',
        r'sale',
        r'discount'
    ]
    return any(re.search(pattern, content.lower()) for pattern in spam_patterns)

@login_required
@rate_limit('comment', limit=5, period=60)  # 1分間に5コメントまで
def reply_comment(request, comment_id):
    if request.method == 'POST':
        parent_comment = get_object_or_404(Comment, id=comment_id)
        content = request.POST.get('content')
        
        if check_spam(content):
            raise ValidationError('スパムと判定されました')
            
        # 同じ内容の投稿を制限
        cache_key = f'comment_{request.user.id}_{hashlib.md5(content.encode()).hexdigest()}'
        if cache.get(cache_key):
            raise ValidationError('同じ内容を連続で投稿することはできません')
        cache.set(cache_key, True, 300)  # 5分間同じ内容の投稿を制限
        if content:
            # XSS対策としてHTMLエスケープ
            content = escape(content)
            Comment.objects.create(
                video=parent_comment.video,
                user=request.user,
                content=content,
                parent=parent_comment
            )
    return redirect('gametube:video_detail', video_id=parent_comment.video.id)

@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
        liked = False
    else:
        comment.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'likes_count': comment.likes.count()})

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user == request.user:
        comment.delete()
    return redirect('gametube:video_detail', video_id=comment.video.id)

@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST' and comment.user == request.user:
        content = request.POST.get('content')
        if content:
            comment.content = content
            comment.save()
    return redirect('gametube:video_detail', video_id=comment.video.id)