from django.contrib import admin
from .models import Video, Comment, GameDownload, DevicePurchase

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploader', 'views', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('created_at', 'uploader')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'created_at')
    search_fields = ('content',)
    list_filter = ('created_at',)

@admin.register(GameDownload)
class GameDownloadAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'uploader', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('category', 'created_at')

@admin.register(DevicePurchase)
class DevicePurchaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'uploader', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('category', 'created_at')