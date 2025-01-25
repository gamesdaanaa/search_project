# Generated by Django 4.2.12 on 2025-01-25 03:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gametube', '0006_chatmessage_image_alter_userprofile_age'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameboard',
            name='age_restriction',
            field=models.CharField(choices=[('all', '制限なし'), ('r15', '15歳以上'), ('r18', '18歳以上')], default='all', max_length=5),
        ),
    ]
