from pathlib import Path
import os
import dj_database_url  # pip install dj-database-url

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Security / env ---
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

# Examples:
# ALLOWED_HOSTS=".onrender.com"
# CSRF_TRUSTED_ORIGINS="https://*.onrender.com"
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split()
CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS", "").split()

# --- Apps ---
INSTALLED_APPS = [
    "drf_spectacular",
    "rest_framework",
    "widget_tweaks",
    "channels",
    "chat",
    "courses",
    "dashboard",
    "accounts",
    # "cloudinary",           # Cloudinary (media)
    # "cloudinary_storage",   # Cloudinary (media)
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

# --- Middleware (Whitenoise right after security) ---
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "elearning_platform.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "dashboard.context_processors.merged_notifications",
            ],
        },
    },
]

WSGI_APPLICATION = "elearning_platform.wsgi.application"
ASGI_APPLICATION = "elearning_platform.asgi.application"

# --- Database (Render provides DATABASE_URL) ---
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR/'db.sqlite3'}",
        conn_max_age=600,
        ssl_require=True,
    )
}

# --- DRF / schema ---
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

if not DEBUG:
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
        "rest_framework.renderers.JSONRenderer",
    ]

SPECTACULAR_SETTINGS = {
    "TITLE": "eLearning Platform API",
    "DESCRIPTION": "Auto-generated API docs for the eLearning coursework.",
    "VERSION": "1.0.0",
}

# --- Auth / redirects ---
AUTH_USER_MODEL = "accounts.CustomUser"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/accounts/login/"
# # Static files
# --- Static / WhiteNoise ---
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Configure STATICFILES_DIRS to point to your static directory
STATICFILES_DIRS = [BASE_DIR / "static"]

# Debug static files during deployment
print(f"DEBUG: BASE_DIR = {BASE_DIR}")
print(f"DEBUG: STATIC_URL = {STATIC_URL}")
print(f"DEBUG: STATIC_ROOT = {STATIC_ROOT}")
print(f"DEBUG: STATICFILES_DIRS = {STATICFILES_DIRS}")

import os
static_path = BASE_DIR / "static"
if static_path.exists():
    print(f"DEBUG: Static directory exists at {static_path}")
    for root, dirs, files in os.walk(static_path):
        for file in files:
            filepath = os.path.join(root, file)
            print(f"DEBUG: Found static file: {filepath}")
else:
    print(f"DEBUG: Static directory does NOT exist at {static_path}")

# Modern STORAGES configuration (Django 4.2+)
# Removed STATICFILES_STORAGE to avoid conflicts
USE_CLOUDINARY = bool(os.environ.get("CLOUDINARY_URL")) and not DEBUG

if USE_CLOUDINARY:
    STORAGES = {
        "default": {"BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage"},
        "staticfiles": {"BACKEND": "whitenoise.storage.StaticFilesStorage"},
    }
    MEDIA_URL = "/media/"
    CLOUDINARY_STORAGE = {"RAW_UPLOAD": True}
else:
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "whitenoise.storage.StaticFilesStorage"},
    }

# Optional leniency for WhiteNoise
WHITENOISE_MANIFEST_STRICT = False
# --- Passwords ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Channels / Redis (Render: set REDIS_URL) ---
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [os.environ.get("REDIS_URL", "redis://127.0.0.1:6379")]},
    }
}

# --- Email (dev) ---
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "noreply@example.com"

# --- I18N ---
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --- Security for Render’s proxy ---
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# --- Defaults ---
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
