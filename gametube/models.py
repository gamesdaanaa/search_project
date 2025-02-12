from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)

from django.db import models
from django.contrib.auth.models import User

class Video(models.Model):
    AGE_RESTRICTION_CHOICES = [
        ('under18', '18歳未満'),
        ('over18', '18歳以上'),
    ]

    CATEGORY_CHOICES = [
        ('new_game', '新規ゲーム'),
        ('fps_game', 'FPSゲーム'),
        ('gaming_device', 'ゲーミングデバイス'),
        ('action_game', 'アクションゲーム'),
        ('adventure_game', 'アドベンチャーゲーム'),
        ('rpg_game', 'RPGゲーム'),
        ('simulation_game', 'シミュレーションゲーム'),
        ('sports_game', 'スポーツゲーム'),
        ('racing_game', 'レーシングゲーム'),
        ('puzzle_game', 'パズルゲーム'),
        ('rhythm_game', 'リズムゲーム'),
        ('mmo_game', 'MMOゲーム'),
        ('horror_game', 'ホラーゲーム'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    video_file = models.FileField(upload_to='videos/')
    thumbnail = models.ImageField(upload_to='thumbnails/')
    uploader = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.IntegerField(default=0)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    age_restriction = models.CharField(max_length=7, choices=AGE_RESTRICTION_CHOICES, default='all')
    likes = models.ManyToManyField(User, related_name='liked_videos', blank=True)

    def __str__(self):
        return self.title



class Comment(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)

    def __str__(self):
        return f'{self.user.username} on {self.video.title}'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    age = models.IntegerField(null=False, default=13)

    def __str__(self):
        return self.user.username

class Subscription(models.Model):
    subscriber = models.ForeignKey(User, related_name='subscriptions', on_delete=models.CASCADE)
    channel = models.ForeignKey(User, related_name='subscribers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('subscriber', 'channel')

    def __str__(self):
        return f'{self.subscriber.username} -> {self.channel.username}'

class GameDownload(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=Video.CATEGORY_CHOICES)
    thumbnail = models.ImageField(upload_to='game_thumbnails/')
    url = models.URLField()
    uploader = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



class DevicePurchase(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=Video.CATEGORY_CHOICES)
    thumbnail = models.ImageField(upload_to='device_thumbnails/')
    url = models.URLField()
    uploader = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class GameBoard(models.Model):
    AGE_RESTRICTION_CHOICES = [
        ('under18', '18歳未満'),
        ('over18', '18歳以上'),
    ]

    game = models.CharField(max_length=100)
    age_restriction = models.CharField(max_length=7, choices=AGE_RESTRICTION_CHOICES, default='all')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.game

class ChatMessage(models.Model):
    board = models.ForeignKey(GameBoard, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    image = models.ImageField(upload_to='chat_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.message}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.message}"


class WatchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    watched_at = models.DateTimeField(auto_now=True)
    watch_duration = models.IntegerField(default=0)  # 視聴時間（秒）

    class Meta:
        ordering = ['-watched_at']

    def __str__(self):
        return f"{self.user.username} watched {self.video.title}"

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'video')

    def __str__(self):
        return f"{self.user.username} liked {self.video.title}"


