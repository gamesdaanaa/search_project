from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from .models import Video, UserProfile, Comment, Subscription, Like

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
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('gametube:home')
        else:
            messages.error(request, 'Invalid username or password')
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

