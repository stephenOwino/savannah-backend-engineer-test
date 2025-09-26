import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config(
    "SECRET_KEY",
    default="django-insecure-8b=i_xn&9!d89u^ozb@*dd(0mjn4d&p38ud$^80%xza=l%t@rd",
)
DEBUG = config("DEBUG", default=True, cast=bool)

# More restrictive ALLOWED_HOSTS for production
if DEBUG:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = config(
        "ALLOWED_HOSTS",
        default="localhost,127.0.0.1",
        cast=lambda v: [s.strip() for s in v.split(",")],
    )

# Applications
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "api",
    "rest_framework",
    "mozilla_django_oidc",  # OIDC client
    "corsheaders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    # "mozilla_django_oidc.middleware.SessionRefresh",  # Temporarily commented out
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "savannah_assess.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # Add templates directory
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

WSGI_APPLICATION = "savannah_assess.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB", default="savannadb"),
        "USER": config("POSTGRES_USER", default="postgres"),
        "PASSWORD": config("POSTGRES_PASSWORD", default=""),
        "HOST": config("DB_HOST", default="postgres_db"),
        "PORT": config("POSTGRES_PORT", default="5432"),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Authentication backends
AUTHENTICATION_BACKENDS = (
    "mozilla_django_oidc.auth.OIDCAuthenticationBackend",
    "django.contrib.auth.backends.ModelBackend",
)

# DRF config - Updated for better OIDC integration
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "mozilla_django_oidc.contrib.drf.OIDCAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",  # Fallback
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}

# Africa's Talking
AFRICASTALKING_USERNAME = config("AFRICASTALKING_USERNAME", default="sandbox")
AFRICASTALKING_API_KEY = config("AFRICASTALKING_API_KEY", default=None)
AFRICASTALKING_SENDER_ID = config("AFRICASTALKING_SENDER_ID", default="")
ADMIN_EMAIL = config("ADMIN_EMAIL", default="stephenowin233@gmail.com")
EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- OIDC AUTH CONFIG (mozilla-django-oidc) ---
import logging

logger = logging.getLogger(__name__)

OIDC_OP_DOMAIN = config("OIDC_OP_DOMAIN")
OIDC_RP_CLIENT_ID = config("OIDC_RP_CLIENT_ID")
OIDC_RP_CLIENT_SECRET = config("OIDC_RP_CLIENT_SECRET")

logger.info(f"OIDC_OP_DOMAIN: {OIDC_OP_DOMAIN}")
logger.info(f"OIDC_OP_AUTHORIZATION_ENDPOINT: https://{OIDC_OP_DOMAIN}/authorize")
logger.info(f"OIDC_OP_TOKEN_ENDPOINT: https://{OIDC_OP_DOMAIN}/oauth/token")
logger.info(f"OIDC_OP_JWKS_ENDPOINT: https://{OIDC_OP_DOMAIN}/.well-known/jwks.json")

# Core OIDC endpoints
OIDC_OP_AUTHORIZATION_ENDPOINT = f"https://{OIDC_OP_DOMAIN}/authorize"
OIDC_OP_TOKEN_ENDPOINT = f"https://{OIDC_OP_DOMAIN}/oauth/token"
OIDC_OP_USER_ENDPOINT = f"https://{OIDC_OP_DOMAIN}/userinfo"
OIDC_OP_JWKS_ENDPOINT = f"https://{OIDC_OP_DOMAIN}/.well-known/jwks.json"

# OIDC Settings
OIDC_RP_SIGN_ALGO = "RS256"
OIDC_RP_SCOPES = "openid email profile"
OIDC_CREATE_USER = True
OIDC_UPDATE_USER = True  # Update user info on each login

# Session and token settings
OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS = 3600
OIDC_TOKEN_USE_BASIC_AUTH = False  # Auth0 doesn't require basic auth
OIDC_STORE_ACCESS_TOKEN = True
OIDC_STORE_ID_TOKEN = True

# Custom claims mapping (optional)
OIDC_USERNAME_ALGO = "mozilla_django_oidc.utils.generate_username"

# Redirect URLs
LOGIN_REDIRECT_URL = "/api/landing/"  # Updated to point to authenticated landing
LOGOUT_REDIRECT_URL = "/"
LOGIN_URL = "/oidc/authenticate/"

# --- CORS ---
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOW_CREDENTIALS = True
else:
    CORS_ALLOWED_ORIGINS = config(
        "CORS_ALLOWED_ORIGINS",
        default="http://localhost:3000,http://127.0.0.1:3000",
        cast=lambda v: [s.strip() for s in v.split(",")],
    )
    CORS_ALLOW_CREDENTIALS = True

# Security settings
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "mozilla_django_oidc": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
        },
        "__main__": {  # Capture settings.py logs
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}
