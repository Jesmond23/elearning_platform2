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
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

# Add Cloudinary apps only if configured
USE_CLOUDINARY = bool(os.environ.get("CLOUDINARY_URL"))
if USE_CLOUDINARY:
    INSTALLED_APPS.insert(-7, "cloudinary_storage")  # For static files
    INSTALLED_APPS.insert(-7, "cloudinary")  # Core cloudinary

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

# --- Static Files Configuration ---
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Configure static files storage based on environment
if USE_CLOUDINARY:
    # Import cloudinary for configuration
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    
    # Parse CLOUDINARY_URL for explicit configuration
    cloudinary_url = os.environ.get("CLOUDINARY_URL")
    if cloudinary_url:
        # Extract components from cloudinary://api_key:api_secret@cloud_name
        import urllib.parse
        parsed = urllib.parse.urlparse(cloudinary_url)
        
        # Configure Cloudinary explicitly
        cloudinary.config(
            cloud_name=parsed.hostname,
            api_key=parsed.username,
            api_secret=parsed.password,
            secure=True  # Always use HTTPS
        )
    
    STORAGES = {
        "default": {
            "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
        },
    }
    
    # Cloudinary storage settings
    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": cloudinary.config().cloud_name,
        "API_KEY": cloudinary.config().api_key,
        "API_SECRET": cloudinary.config().api_secret,
        "SECURE": True,
        "MEDIA_TAG": "media",  # Tag all media uploads
        "INVALID_VIDEO_ERROR_MESSAGE": "Please upload a valid video file.",
        "EXCLUDE_DELETE_ORPHANED_MEDIA_PATHS": (),
        "STATICFILES_MANIFEST_ROOT": os.path.join(BASE_DIR, 'staticfiles'),
        "MAGIC_FILE_PATH": "uploads/",  # Organize uploads in a folder
    }
    
    # Don't set MEDIA_URL when using Cloudinary - it handles URLs automatically
else:
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
        },
    }
    # Only set MEDIA_URL and MEDIA_ROOT when NOT using Cloudinary
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"

# WhiteNoise configuration
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_USE_FINDERS = True  # Helps during development

# --- Debug prints (remove in production) ---
if DEBUG:
    print(f"DEBUG: BASE_DIR = {BASE_DIR}")
    print(f"DEBUG: STATIC_URL = {STATIC_URL}")
    print(f"DEBUG: STATIC_ROOT = {STATIC_ROOT}")
    print(f"DEBUG: STATICFILES_DIRS = {STATICFILES_DIRS}")
    print(f"DEBUG: USE_CLOUDINARY = {USE_CLOUDINARY}")
    
    if USE_CLOUDINARY:
        print(f"DEBUG: Cloudinary cloud_name = {cloudinary.config().cloud_name}")
        print(f"DEBUG: Cloudinary configured = {bool(cloudinary.config().cloud_name)}")
    else:
        print(f"DEBUG: MEDIA_URL = {MEDIA_URL}")
        print(f"DEBUG: MEDIA_ROOT = {MEDIA_ROOT}")
    
    static_path = BASE_DIR / "static"
    if static_path.exists():
        print(f"DEBUG: Static directory exists at {static_path}")
        for root, dirs, files in os.walk(static_path):
            for file in files:
                filepath = os.path.join(root, file)
                print(f"DEBUG: Found static file: {filepath}")
    else:
        print(f"DEBUG: Static directory does NOT exist at {static_path}")

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

# --- Security for Render's proxy ---
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# --- Defaults ---
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"