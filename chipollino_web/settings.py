"""
Django settings for chipollino_web project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path

import chipollino_web.env as env

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-w2w*9q7o1@e@)vn#wa5c0lio28*lztdfx9zv39t9m@w&*#9elt"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.DJANGO_DEBUG

ALLOWED_HOSTS = [ "chipollino.flygrounder.ru", "localhost" ]

CSRF_TRUSTED_ORIGINS = ['https://chipollino.flygrounder.ru']

X_FRAME_OPTIONS = 'SAMEORIGIN'


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'accounts',
    "converter.apps.ConverterConfig",
    "Chipollino",
    "latex2mathml"
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "chipollino_web.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "chipollino_web.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DB_NAME = Path(env.DJANGO_DB) if env.DJANGO_DB is not None else BASE_DIR / "db.sqlite3"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DB_NAME,
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "/static/"

STATICFILES_DIRS = [
   BASE_DIR /  "static",
   BASE_DIR / "config",
]

STATIC_ROOT = BASE_DIR / "collected_static"

if DEBUG:
    CONFIG_DIR = BASE_DIR / 'config'
else:
    CONFIG_DIR = STATIC_ROOT

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

import sys
sys.path.append("converter/src")

# sessions settings
SESSION_EXPIRE_AT_BROWSER_CLOSE= False
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True
SESSION_COOKIE_AGE = 60 * 60 * 24 * 2 # 2 дня
SESSION_EXPIRE_SECONDS = 60 * 60 * 24 * 2
