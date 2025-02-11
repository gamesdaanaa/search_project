"""
Django settings for myproject project.
"""

import os
from pathlib import Path
import psycopg2
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-your-secret-key')

# SECURITY WARNING: don't run with debug turned on in production!


DEBUG = False
ALLOWED_HOSTS = ['*', '.repl.co', '.replit.dev', '.replit.app']

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = True
CSRF_COOKIE_DOMAIN = None
CSRF_TRUSTED_ORIGINS = [
    'https://*.replit.app',
    'https://*.repl.co'
]
# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'gametube',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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

# ファイルのトップレベルでインポート
# データベース接続情報
DB_HOST = os.getenv('DB_HOST', '')
DB_NAME = os.getenv('DB_NAME', '')
DB_USER = os.getenv('DB_USER', '')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_PORT = os.getenv('DB_PORT', 5432)

connection = None  # 初期化
cursor = None  # cursor を定義

try:
    # データベースに接続
    connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    cursor = connection.cursor()
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    print(f"Connected to PostgreSQL database. Version: {db_version[0]}") if db_version else "Connected to PostgreSQL database. Version information not available."
except Exception as e:
    print(f"Error connecting to PostgreSQL: {e}")
finally:
    if connection:
        # Cursor が存在する場合にのみクローズ
        if cursor:
            cursor.close()
        connection.close()
        print("Database connection closed.")
# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gametube',
        'USER': 'myapp_db_owner',
        'PASSWORD': 'zGZKSAn4J9Bl',
        'HOST': 'ep-jolly-waterfall-a1owq4gt-pooler.ap-southeast-1.aws.neon.tech',
        'PORT': '5432',
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
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# 管理サイト用のカスタムスタイル
ADMIN_SITE_HEADER = "GameTube 管理サイト"
ADMIN_SITE_TITLE = "GameTube Admin"
ADMIN_INDEX_TITLE = "サイト管理"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

if not DEBUG:
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    MEDIA_ROOT = BASE_DIR / 'mediafiles'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'