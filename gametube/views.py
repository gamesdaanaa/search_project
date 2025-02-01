
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Video, UserProfile, Like, Comment, Subscription

def home(request):
    videos = Video.objects.all().order_by('-created_at')
    return render(request, 'gametube/home.html', {'videos': videos})
