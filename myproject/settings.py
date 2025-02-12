"""
Django settings for myproject project.
"""

import os
from pathlib import Path
import psycopg2
import datetime
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-your-secret-key')

# SECURITY WARNING: don't run with debug turned on in production!


DEBUG = True
ALLOWED_HOSTS = ['*', '.repl.co', '.replit.dev', '.replit.app', '.pike.replit.dev']

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_HOST = None
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = None
CSRF_USE_SESSIONS = False
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_DOMAIN = None

CSRF_TRUSTED_ORIGINS = [
    'https://*.replit.dev',
    'https://*.pike.replit.dev',
    'https://*.repl.dev',
    'https://*.replit.dev:*',
    'https://*.pike.replit.dev:*',
    'https://fb106892-b31d-407e-b484-e318f22fe67f-00-2wtm6tsyubq8a.pike.replit.dev',
    'https://fb106892-b31d-407e-b484-e318f22fe67f-00-2wtm6tsyubq8a.pike.replit.dev:3000',
    'https://fb106892-b31d-407e-b484-e318f22fe67f-00-2wtm6tsyubq8a.pike.replit.dev:*'
]

# CSRF設定の最適化
CSRF_COOKIE_SECURE = False  # Development setting
CSRF_USE_SESSIONS = False
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = None

# セキュリティ設定の最適化
CSRF_COOKIE_SECURE = False  # Development setting
CSRF_USE_SESSIONS = True
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = None
CSRF_TRUSTED_ORIGINS_ONLY = False


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_otp',
    'django_otp.plugins.otp_totp',
    'gametube',
]

# reCAPTCHA settings
RECAPTCHA_PUBLIC_KEY = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
RECAPTCHA_PRIVATE_KEY = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'
SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']

# JWT settings
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_DELTA = datetime.timedelta(days=1)

# 2FA settings
OTP_TOTP_ISSUER = 'GameTube'

MIDDLEWARE = [
    'gametube.middleware.WAFMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'gametube.middleware.SecurityMonitoringMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOWED_ORIGINS = ['https://fb106892-b31d-407e-b484-e318f22fe67f-00-2wtm6tsyubq8a.pike.replit.dev',]
ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myproject.wsgi.application'

# データベース接続情報（環境変数から取得）
DB_HOST = os.getenv('PGHOST')
DB_NAME = os.getenv('PGDATABASE')
DB_USER = os.getenv('PGUSER')
DB_PASSWORD = os.getenv('PGPASSWORD')
DB_PORT = os.getenv('PGPORT', '5432')  # 文字列として取得

# 必須の環境変数が設定されているか確認
if not all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
    print(f"Missing environment variables: HOST={DB_HOST}, NAME={DB_NAME}, USER={DB_USER}")
    raise ValueError("必要なデータベース環境変数が設定されていません。")

# PostgreSQL接続の確認
connection = None
cursor = None

try:
    # データベースに接続
    connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=int(DB_PORT),  # 整数に変換
        sslmode="require"
    )
    cursor = connection.cursor()

    # バージョン情報の取得
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()


    print(f"Connected to PostgreSQL database. Version: {db_version[0]}") if db_version else "Connected to PostgreSQL database. Version information not available."
except Exception as e:
    print(f"Error connecting to PostgreSQL: {e}")
finally:
    if cursor:
        cursor.close()
    if connection:
        connection.close()
        print("Database connection closed.")

# Django 用 DATABASES 設定
DATABASES = {
'default': {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': DB_NAME,
    'USER': DB_USER,
    'PASSWORD': DB_PASSWORD,
    'HOST': DB_HOST,
    'PORT': int(DB_PORT),  # Djangoでも整数に変換
    'OPTIONS': {
        'sslmode': 'require',
    },
}
}

# Security Headers
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
CSP_DEFAULT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_FONT_SRC = ("'self'", "https:", "data:")

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 10,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'gametube.validators.SymbolValidator',
    },
    {
        'NAME': 'gametube.validators.UpperLowerValidator',
    },
]

# セッションセキュリティ設定
SESSION_COOKIE_AGE = 3600  # 1時間でセッション期限切れ
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # ブラウザを閉じたらセッション終了
SESSION_COOKIE_SECURE = True  # HTTPSのみ
SESSION_COOKIE_HTTPONLY = True  # JavaScriptからアクセス不可

# セキュリティヘッダー
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CSP設定の強化
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "'unsafe-eval'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_FONT_SRC = ("'self'", "https:", "data:")

# レートリミット設定
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'
RATELIMIT_FAIL_OPEN = False
RATELIMIT_VIEW_RATE = '30/m'  # 1分間に30回までのアクセス制限
RATELIMIT_LOGIN_RATE = '5/m'  # ログイン試行は1分間に5回まで
RATELIMIT_BLOCK_TIME = 900    # ブロック時間15分
RATELIMIT_API_RATE = '100/m'  # API制限は1分間に100回まで

# パスワードの複雑さ要件
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
]

# セッションセキュリティ
SESSION_COOKIE_AGE = 3600  # 1時間でセッション期限切れ
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# ログイン試行回数制限
AXES_ENABLED = True
AXES_FAILURE_LIMIT = 5  # 5回失敗でロック
AXES_COOLOFF_TIME = 1  # 1時間のロック時間
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True

# セキュリティヘッダー設定
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

LANGUAGE_CODE = 'ja'
TIME_ZONE = 'Asia/Tokyo'
USE_I18N = True
USE_TZ = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'verbose',
        },
        'security': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'security.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.security': {
            'handlers': ['security'],
            'level': 'INFO',
            'propagate': True,
        },
        'gametube.security': {
            'handlers': ['security'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# AWS S3設定
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'ap-northeast-1')
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/media/'
MEDIA_ROOT = BASE_DIR / 'media'

if not DEBUG:
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    MEDIA_ROOT = BASE_DIR / 'mediafiles'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

