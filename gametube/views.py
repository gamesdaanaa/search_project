from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from .models import Video, UserProfile, Comment, Subscription, Like
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver

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


@login_required
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
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

@login_required
def upload_video(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        video_file = request.FILES.get('video')
        thumbnail = request.FILES.get('thumbnail')
        category = request.POST.get('category')
        age_restriction = request.POST.get('age_restriction')

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

@login_required
def reply_comment(request, comment_id):
    if request.method == 'POST':
        parent_comment = get_object_or_404(Comment, id=comment_id)
        content = request.POST.get('content')
        if content:
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