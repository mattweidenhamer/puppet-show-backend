"""
Django settings for puppetshowsite project.

Generated by 'django-admin startproject' using Django 4.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
import environ
import logging
from datetime import datetime
from pathlib import Path

os.makedirs(os.path.dirname("./logs/"), exist_ok=True)


logger = logging.getLogger(__name__)

env = environ.Env()
environ.Env.read_env()


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG") in ["True", "true", "TRUE", "1"]
if DEBUG:
    logger.warn("EnVar DEBUG is True! Running in development mode.")

assert (DEBUG is False) or (DEBUG is True), "DEBUG must be a boolean value"

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")


ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "puppetshowapp.apps.PuppetshowappConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "puppetshowsite.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
            ],
        },
    },
]

WSGI_APPLICATION = "puppetshowsite.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
DATABASES = (
    {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
    if DEBUG
    else {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": env("DB_NAME"),
            "USER": env("DB_USER"),
            "PASSWORD": env("DB_PASSWORD"),
            "HOST": env("DB_HOST"),
            "PORT": env("DB_PORT"),
        }
    }
)


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "EST"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "puppetshowapp.backends.DiscordAuthBackend",
)

SITE_ID = 1
# ACCOUNT_EMAIL_REQUIRED = True
# ACCOUNT_SESSION_REMEMBER = True
# ACCOUNT_AUTHENTICATION_METHOD = "email"
# ACCOUNT_UNIQUE_EMAIL = True

REST_FRAMEWORK = {
    "DATETIME_FORMAT": "%m/%d/%y %I:%M%P",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication"
    ],
}

# Media

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media/")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "loggers": {
        "": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
        },
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": f"{os.path.join('logs', datetime.now().strftime('%Y-%m-%d %H-%M-%S'))}.log",
            "when": "midnight",
            "level": "DEBUG",
            "formatter": "verbose",
        },
    },
    "formatters": {
        "verbose": {
            "format": "{name} {levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
}


CORS_ALLOWED_ORIGINS = ["http://localhost:3000", "http://3.13.108.33:3000"]

AUTH_USER_MODEL = "puppetshowapp.DiscordPointingUser"
AUTH_USER_MODEL_MANAGER = "puppetshowapp.DiscordPointingUserManager"

FRONTEND = env("FRONTEND_DEBUG") if DEBUG else env("FRONTEND_PROD")
BACKEND = env("BACKEND_DEBUG") if DEBUG else env("BACKEND_PROD")

DISCORD = {
    "URLS": {
        "AUTH": env("AUTH_URL"),
        "TOKEN": env("TOKEN_URL"),
        "API_ENDPOINT": env("API_ENDPOINT"),
        "OAUTH": env("DEBUG_OAUTH_URL") if DEBUG else env("PROD_OAUTH_URL"),
        "CALLBACK": f"{BACKEND}/callback/",
    },
    "CLIENT_ID": env("CLIENT_ID"),
    "CLIENT_SECRET": env("CLIENT_SECRET"),
    "BOT_TOKEN": env("BOT_TOKEN"),
}       