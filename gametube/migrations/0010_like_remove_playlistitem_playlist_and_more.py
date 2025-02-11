# Generated by Django 4.2.12 on 2025-02-11 13:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gametube', '0009_playlist_watchhistory_watch_duration_playlistitem_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gametube.video')),
            ],
            options={
                'unique_together': {('user', 'video')},
            },
        ),
        migrations.RemoveField(
            model_name='playlistitem',
            name='playlist',
        ),
        migrations.RemoveField(
            model_name='playlistitem',
            name='video',
        ),
        migrations.DeleteModel(
            name='Playlist',
        ),
        migrations.DeleteModel(
            name='PlaylistItem',
        ),
    ]
