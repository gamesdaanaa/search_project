from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q
from .models import Video, Comment, Subscription, UserProfile, GameDownload, DevicePurchase, GameBoard, ChatMessage, Notification, WatchHistory

def home(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')

    videos = Video.objects.all()

    if request.user.is_authenticated:
        user_age = request.user.userprofile.age
        if user_age:
            if user_age < 15:
                videos = videos.filter(age_restriction='all')
            elif user_age < 18:
                videos = videos.exclude(age_restriction='r18')
    else:
        videos = videos.filter(age_restriction='all')

    if query:
        videos = videos.filter(title__icontains=query)
        users = User.objects.filter(username__icontains=query)
        return render(request, 'gametube/home.html', {
            'videos': videos,
            'users': users,
            'query': query
        })

    if category:
        videos = videos.filter(category=category)

    videos = videos.order_by('-created_at')
    return render(request, 'gametube/home.html', {'videos': videos, 'query': query})

from django.http import StreamingHttpResponse, HttpResponse
from wsgiref.util import FileWrapper
import os

def video_detail(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    video.views += 1
    video.save()

    if request.user.is_authenticated:
        WatchHistory.objects.create(user=request.user, video=video)
    if 'range' in request.headers:
        path = video.video_file.path
        file_size = os.path.getsize(path)
        chunk_size = 8192
        start, end = request.headers['range'].replace('bytes=', '').split('-')
        start = int(start)
        end = int(end) if end else file_size - 1
        length = end - start + 1

        response = StreamingHttpResponse(
            FileWrapper(open(path, 'rb'), chunk_size),
            status=206,
            content_type='video/mp4'
        )
        response['Content-Length'] = str(length)
        response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
        return response
    comments = Comment.objects.filter(video=video).order_by('-created_at')

    if request.method == 'POST' and request.user.is_authenticated:
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                video=video,
                user=request.user,
                content=content
            )
            return redirect(request.path + '#comments')

    related_videos = Video.objects.exclude(id=video_id).order_by('-created_at')[:5]
    return render(request, 'gametube/video_detail.html', {
        'video': video,
        'comments': comments,
        'related_videos': related_videos
    })



@login_required
def upload_video(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        video_file = request.FILES.get('video_file')
        thumbnail = request.FILES.get('thumbnail')

        category = request.POST.get('category')
        if title and video_file and thumbnail and category:
            Video.objects.create(
                title=title,
                description=description,
                video_file=video_file,
                thumbnail=thumbnail,
                category=category,
                uploader=request.user
            )
            return redirect('gametube:home')

    return render(request, 'gametube/upload.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('gametube:home')
    return render(request, 'gametube/login.html')

def logout_view(request):
    logout(request)
    return redirect('gametube:home')

from django.http import JsonResponse

@login_required
def like_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    is_liked = request.user in video.likes.all()

    if is_liked:
        video.likes.remove(request.user)
    else:
        video.likes.add(request.user)

    return JsonResponse({
        'likes_count': video.likes.count(),
        'is_liked': not is_liked
    })

def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile, created = UserProfile.objects.get_or_create(user=profile_user)
    videos = Video.objects.filter(uploader=profile_user).order_by('-created_at')
    is_subscribed = False
    subscribers_count = profile_user.subscribers.count()

    if request.method == 'POST' and request.user == profile_user:
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
            profile.save()
        if 'bio' in request.POST:
            profile.bio = request.POST['bio']
        if 'age' in request.POST:
            profile.age = request.POST['age']
        profile.save()
        return redirect('gametube:user_profile', username=username)

    if request.user.is_authenticated:
        is_subscribed = Subscription.objects.filter(
            subscriber=request.user,
            channel=profile_user
        ).exists()

    return render(request, 'gametube/user_profile.html', {
        'profile_user': profile_user,
        'videos': videos,
        'is_subscribed': is_subscribed,
        'subscribers_count': subscribers_count
    })

@login_required
def subscribe(request, username):
    channel = get_object_or_404(User, username=username)

    if request.user != channel:
        subscription, created = Subscription.objects.get_or_create(
            subscriber=request.user,
            channel=channel
        )
        if not created:
            subscription.delete()

    return JsonResponse({
        'subscribed': created if request.user != channel else False,
        'subscribers_count': channel.subscribers.count()
    })

@login_required
def subscriptions(request):
    subscriptions = Subscription.objects.filter(subscriber=request.user)
    return render(request, 'gametube/subscriptions.html', {
        'subscriptions': subscriptions
    })

@login_required
def game_downloads(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        thumbnail = request.FILES.get('thumbnail')
        url = request.POST.get('url')

        GameDownload.objects.create(
            title=title,
            description=description,
            category=category,
            thumbnail=thumbnail,
            url=url,
            uploader=request.user
        )
        return redirect('gametube:game_downloads')

    query = request.GET.get('q', '')
    downloads = GameDownload.objects.all()
    if query:
        downloads = downloads.filter(title__icontains=query)
    downloads = downloads.order_by('-created_at')
    return render(request, 'gametube/game_downloads.html', {'downloads': downloads, 'query': query})

@login_required
def device_purchases(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        thumbnail = request.FILES.get('thumbnail')
        url = request.POST.get('url')

        DevicePurchase.objects.create(
            title=title,
            description=description,
            category=category,
            thumbnail=thumbnail,
            url=url,
            uploader=request.user
        )
        return redirect('gametube:device_purchases')

    query = request.GET.get('q', '')
    devices = DevicePurchase.objects.all()
    if query:
        devices = devices.filter(title__icontains=query)
    devices = devices.order_by('-created_at')
    return render(request, 'gametube/device_purchases.html', {'devices': devices, 'query': query})

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        age = request.POST.get('age')

        if password1 != password2:
            return render(request, 'gametube/register.html', {'error': 'パスワードが一致しません'})

        if User.objects.filter(username=username).exists():
            return render(request, 'gametube/register.html', {'error': 'このユーザー名は既に使用されています'})

        try:
            user = User.objects.create_user(username=username, password=password1)

            # UserProfileは signals.pyで自動作成されるため、既存のプロフィールを取得
            profile = UserProfile.objects.get(user=user)

            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']

            if 'bio' in request.POST and request.POST['bio']:
                profile.bio = request.POST['bio']

            if age:
                profile.age = age

            profile.save()
            login(request, user)
            return redirect('gametube:home')

        except Exception as e:
            if user:
                user.delete()
            return render(request, 'gametube/register.html', {'error': 'アカウント作成に失敗しました'})

    return render(request, 'gametube/register.html')

@login_required
def game_boards(request):
    if request.method == 'POST':
        game = request.POST.get('game')
        delete_id = request.POST.get('delete')
        age_restriction = request.POST.get('age_restriction', 'all')
        if game:
            board = GameBoard.objects.create(
                game=game,
                age_restriction=age_restriction
            )
            # 掲示板作成時に全ユーザーに通知を送信
            for user in User.objects.all():
                Notification.objects.create(
                    user=user,
                    message=f'新しい掲示板「{board.game}」が作成されました',
                    link=f'/board/{board.id}/'
                )
        elif delete_id and (request.user.is_superuser or request.user.is_staff):
            GameBoard.objects.filter(id=delete_id).delete()

    query = request.GET.get('q', '')
    boards = GameBoard.objects.all()
    if request.user.is_authenticated:
        user_age = request.user.userprofile.age
        if user_age < 18:
            boards = boards.filter(age_restriction='under18')
        else:
            boards = boards.all()
    else:
        boards = boards.filter(age_restriction='all')

    if query:
        boards = boards.filter(game__icontains=query)
    boards = boards.order_by('-created_at')
    return render(request, 'gametube/game_boards.html', {
        'boards': boards,
        'can_delete': request.user.is_superuser or request.user.is_staff
    })

@login_required
def board_detail(request, board_id):
    board = get_object_or_404(GameBoard, id=board_id)
    user_age = request.user.userprofile.age

    if board.age_restriction == 'r18' and user_age < 18:
        return redirect('gametube:game_boards')
    elif board.age_restriction == 'r15' and user_age < 15:
        return redirect('gametube:game_boards')
    if request.method == 'POST':
        message = request.POST.get('message')
        image = request.FILES.get('image')
        if message or image:
            ChatMessage.objects.create(
                board=board,
                user=request.user,
                message=message,
                image=image
            )
    query = request.GET.get('q', '')
    messages = ChatMessage.objects.filter(board=board)
    if query:
        messages = messages.filter(message__icontains=query)
    messages = messages.order_by('-created_at')
    return render(request, 'gametube/game_board.html', {
        'board': board,
        'messages': messages,
        'query': query
    })

@receiver(post_save, sender=Video)
def create_video_notification(sender, instance, created, **kwargs):
    if created:
        subscribers = instance.uploader.subscribers.all()
        for subscription in subscribers:
            Notification.objects.create(
                user=subscription.subscriber,
                message=f'{instance.uploader.username}が新しい動画「{instance.title}」を投稿しました',
                link=f'/video/{instance.id}/'
            )

@receiver(post_save, sender=GameBoard)
def create_board_notification(sender, instance, created, **kwargs):
    if created:
        for user in User.objects.all():
            if user.is_authenticated:
                Notification.objects.create(
                    user=user,
                    message=f'新しい掲示板「{instance.game}」が作成されました',
                    link=f'/board/{instance.id}/'
                )

@login_required
@login_required
def reply_comment(request, comment_id):
    parent_comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                video=parent_comment.video,
                user=request.user,
                content=content,
                parent=parent_comment
            )
    return redirect(f'gametube:video_detail/{parent_comment.video.id}#comment-{comment_id}')

@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
        is_liked = False
    else:
        comment.likes.add(request.user)
        is_liked = True
    return JsonResponse({
        'likes_count': comment.likes.count(),
        'is_liked': is_liked
    })

def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'success': True})
@login_required
def liked_videos(request):
    liked_videos = Video.objects.filter(likes=request.user).order_by('-created_at')
    return render(request, 'gametube/liked_videos.html', {'videos': liked_videos})
@login_required
def watch_history(request):
    history = WatchHistory.objects.filter(user=request.user).select_related('video')
    return render(request, 'gametube/watch_history.html', {'history': history})
@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user.is_superuser or comment.user == request.user:
        comment.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=403)

@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user == comment.user:
        if request.method == 'POST':
            content = request.POST.get('content')
            if content:
                comment.content = content
                comment.save()
        return redirect(request.META.get('HTTP_REFERER', 'gametube:home'))
    return redirect('gametube:home')