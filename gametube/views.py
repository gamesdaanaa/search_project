
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Video, UserProfile, Comment, Subscription

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
