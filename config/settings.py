import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()

# =========================
# CORE
# =========================
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", "0") == "1"
AUTH_USER_MODEL = "accounts.CustomUser"

ALLOWED_HOSTS = os.getenv(
    "DJANGO_ALLOWED_HOSTS",
    "localhost,127.0.0.1"
).split(",")

print(f"\n{ALLOWED_HOSTS = }\n")
print(f"\n{DEBUG = }\n")

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') 
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
# =========================
# APPLICATIONS
# =========================
INSTALLED_APPS = [
    "corsheaders",
    "jazzmin",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_yasg",

    "paytechuz.integrations.django",

    "accounts",
    "courses",
    "course_progress",
]

# =========================
# MIDDLEWARE
# =========================
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if not DEBUG:
    index = INSTALLED_APPS.index("django.contrib.staticfiles")
    INSTALLED_APPS.insert(index, "whitenoise.runserver_nostatic")
    MIDDLEWARE.insert(3, "whitenoise.middleware.WhiteNoiseMiddleware")

# =========================
# CORS
# =========================
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = os.getenv(
    "DJANGO_CORS_ALLOWED_ORIGINS",
    "http://localhost:8000,http://127.0.0.1:8000,http://localhost:8014,http://127.0.0.1:8014"
).split(",")

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# =========================
# CSRF
# =========================
CSRF_TRUSTED_ORIGINS = os.getenv(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    "http://localhost:8000,http://127.0.0.1:8000,http://localhost:8014,http://127.0.0.1:8014"
).split(",")

USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# SECURE_SSL_REDIRECT = False

# =========================
# URLS / TEMPLATES
# =========================
ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# =========================
# DATABASE (SQLite – hozirgi holatingga mos)
# =========================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}

# =========================
# AUTH / JWT
# =========================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "accounts.authentication.CookieJWTAuthentication",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=3),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# =========================
# I18N
# =========================
LANGUAGE_CODE = "uz"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ("uz", _("Uzbek")),
    ("en", _("English")),
    ("ru", _("Russian")),
]

LOCALE_PATHS = [BASE_DIR / "locale"]

# =========================
# STATIC & MEDIA
# =========================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

if not DEBUG:
    STORAGES = {
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
        },
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
            'LOCATION': os.path.join(BASE_DIR, 'media'),
        }
    }


# =========================
# DEFAULTS
# =========================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =========================
# SWAGGER
# =========================
SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": False,
    "DEFAULT_API_URL": os.getenv("DOMAIN_URL", "http://localhost:8014"),
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
        }
    },
}

# =========================
# JAZZMIN
# =========================
JAZZMIN_SETTINGS = {
    "site_title": "Admin",
    "site_header": "Ithouse",
    "site_brand": "It House",
    "welcome_sign": "It House Admin",
}
