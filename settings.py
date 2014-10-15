"""
Django settings for freesage project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(__file__)

PROJECT_ROOT = os.path.dirname(__file__)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^z)m2g_(#s@uga67#p1v7(9ioy2#&!2iudp$nsubtou#pwyn9s'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', True)
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['*']

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'middleware.warning_exception_middleware.ProcessExceptionMiddleware',
)

ROOT_URLCONF = 'urls'

WSGI_APPLICATION = 'ezscrape.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('MVP_DB_NAME', 'ezscrape_db'),
        'USER': os.environ.get('POSTGRES_DB_USER', 'fuiste'),
        'PASSWORD': os.environ.get('POSTGRES_DB_PASS', ''),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Chicago'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = os.environ.get("DJANGO_STATIC_URL", "/static/")

# STATIC_URL = '/static/'

STATIC_ROOT = "staticfiles"

if DEBUG:
    STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static/static_serve/')
    print STATIC_ROOT

STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, "static"),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

APPEND_SLASH = False

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, "templates"),
)

INTERNAL_APPS = [
    'app'
]

EXTERNAL_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'south',
    'django_rq',
    'tastypie',
]

INSTALLED_APPS = INTERNAL_APPS + EXTERNAL_APPS

RQ_QUEUES = {
    'default': {
        'URL': os.getenv('REDISTOGO_URL', 'redis://localhost:6379'), # If you're on Heroku
        'DB': 0,
        'DEFAULT_TIMEOUT': 360,
    },
    'high': {
        'URL': os.getenv('REDISTOGO_URL', 'redis://localhost:6379'), # If you're on Heroku
        'DB': 0,
        'DEFAULT_TIMEOUT': 500,
    },
    'low': {
        'URL': os.getenv('REDISTOGO_URL', 'redis://localhost:6379'), # If you're on Heroku
        'DB': 0,
    }
}

import dj_database_url

db_config =  dj_database_url.config()
if db_config:
    DATABASES["default"] = db_config

