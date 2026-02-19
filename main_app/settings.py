import os
from pathlib import Path
from datetime import timedelta
from decouple import config, Csv

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# --- ENVIRONMENT TOGGLE ---
# Default to True for dev; Set to False in your DigitalOcean Env Vars
DEBUG = config("DEBUG", default=True, cast=bool)

SECRET_KEY = config("SECRET_KEY", default="django-insecure-local-dev-key")

# For local dev, ALLOWED_HOSTS is ['*'].
# In Prod, set ALLOWED_HOSTS=mediguard.utsav56.me,utsav56.me
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*", cast=Csv())

# --- DATABASE CONFIG ---
# Automatically switches based on environment variables
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="mediguard"),
        "USER": config("DB_USER", default="utsav"),
        "PASSWORD": config("DB_PASSWORD", default="mediguard"),
        "HOST": config("DB_HOST", default="127.0.0.1"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

# --- REDIS / CHANNELS ---
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                (
                    config("REDIS_HOST", default="127.0.0.1"),
                    config("REDIS_PORT", default=6379, cast=int),
                )
            ],
        },
    },
}

# --- STATIC & MEDIA ---
# Production uses /root/mediguard/staticfiles (as we discussed for Caddy)
STATIC_URL = "static/"
STATIC_ROOT = config("STATIC_ROOT", default=BASE_DIR / "staticfiles")

ROOT_URLCONF = "main_app.urls"

MEDIA_URL = "/media/"
# Persistent data dir for Podman/DigitalOcean
DATA_DIR = Path(config("DATA_DIR", default=BASE_DIR / "data"))
MEDIA_ROOT = DATA_DIR / "media"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

# --- SECURITY & CORS ---
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Allow all in dev, restrict in prod if needed
CORS_ALLOW_CREDENTIALS = True

# CSRF_TRUSTED_ORIGINS must include the protocol (https://)
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="http://localhost:8000,http://127.0.0.1:8000",
    cast=Csv(),
)

# --- JWT & COOKIES ---
SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ("Bearer",),
    "ACCESS_TOKEN_LIFETIME": timedelta(days=3),
    "ROTATE_REFRESH_TOKENS": True,
    # Set Secure to True in Prod (requires HTTPS)
    "AUTH_COOKIE_SECURE": not DEBUG,
    "AUTH_COOKIE_HTTP_ONLY": True,
    "AUTH_COOKIE_SAMESITE": "Lax",
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]
# REST Framework Configuration
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": (
        # our custom SRE global renderer
        # "core.renderers.GlobalResponseRenderer",
        "rest_framework.renderers.JSONRenderer",
        # "rest_framework.renderers.BrowsableAPIRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FileUploadParser",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "accounts.auth.CustomJWTAuthentication",
        # "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    # "EXCEPTION_HANDLER": "core.exceptions.global_exception_handler",
}

SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ("Bearer",),
    "ACCESS_TOKEN_LIFETIME": timedelta(days=3),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=10),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    # Custom Cookie Settings
    "AUTH_COOKIE": "townspark_access_token",
    "AUTH_COOKIE_REFRESH": "townspark_refresh_token",
    "AUTH_COOKIE_SECURE": False,  # Set to True in production (HTTPS)
    "AUTH_COOKIE_HTTP_ONLY": True,  # Prevents JS from reading the cookie (XSS protection)
    "AUTH_COOKIE_PATH": "/",
    "AUTH_COOKIE_SAMESITE": "Lax",
    "ADMIN_COOKIE": "townspark_admin_token",
    "ADMIN_COOKIE_REFRESH": "townspark_admin_refresh_token",
}


DJOSER = {
    "USER_ID_FIELD": "id",
    "LOGIN_FIELD": "email",
    "USER_CREATE_PASSWORD_RETYPE": False,
    "SEND_ACTIVATION_EMAIL": False,  # Set to True if email backend is configured
    "SEND_CONFIRMATION_EMAIL": False,
    # "SERIALIZERS": {
    #     "user_create": "accounts.serializers.UserCreateSerializer",
    #     "user": "accounts.serializers.UserSerializer",
    #     "current_user": "accounts.serializers.UserSerializer",
    # },
}


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = "static/"
