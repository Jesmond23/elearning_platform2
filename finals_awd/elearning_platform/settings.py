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
    "cloudinary",           # Cloudinary (media)
    "cloudinary_storage",   # Cloudinary (media)
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
# STATIC_URL = "/static/"
# STATIC_ROOT = BASE_DIR / "staticfiles"
# STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []

# # Use non-manifest storage to avoid DRF’s missing font references breaking collectstatic
# STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# # (Keep this too; it’s harmless either way)
# WHITENOISE_MANIFEST_STRICT = False

# WHITENOISE_MANIFEST_STRICT = False
# --- Media (Cloudinary in prod, filesystem in dev) ---
# --- Media (Cloudinary in prod, filesystem in dev) ---
# --- Static base settings ---

# --- Static / WhiteNoise ---
# --- Static / WhiteNoise ---
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Check if static directory exists and configure STATICFILES_DIRS
static_dir = BASE_DIR / "static"
if static_dir.exists():
    STATICFILES_DIRS = [static_dir]
else:
    STATICFILES_DIRS = []

# Legacy setting for backward compatibility with older packages like cloudinary
STATICFILES_STORAGE = "whitenoise.storage.StaticFilesStorage"

# Modern STORAGES configuration (Django 4.2+)
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
