
from django.core.management.base import BaseCommand
from django.conf import settings
import boto3
import datetime
import os

class Command(BaseCommand):
    help = 'バックアップの作成'

    def handle(self, *args, **kwargs):
        # S3へのバックアップ
        s3 = boto3.client('s3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'backup_{timestamp}.sql'
        
        # データベースダンプの作成
        os.system(f'pg_dump -h {settings.DATABASES["default"]["HOST"]} -U {settings.DATABASES["default"]["USER"]} {settings.DATABASES["default"]["NAME"]} > {backup_file}')
        
        # S3にアップロード
        s3.upload_file(backup_file, settings.AWS_STORAGE_BUCKET_NAME, f'backups/{backup_file}')
        
        # ローカルファイルの削除
        os.remove(backup_file)
        
        self.stdout.write(self.style.SUCCESS('バックアップが完了しました'))
