from os import getenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'x-ovvleysc=*$@yyj=@+wx@_)h%@dqgl8wjo#pbjr7&$(2c%82'

DEBUG = getenv("ADMIN") != "PROD"

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'adminsortable2',
    "corsheaders",
    'rest_framework',
    'django_filters',

    'mainapp.admin.MyAdminConfig',  # instead of 'django.contrib.admin'
    'mainapp',
    'botapp',
    'pics'
]


MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

CORS_ALLOWED_ORIGINS = [
    "https://sova.kpi.in.ua",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

ROOT_URLCONF = 'garni_studenti.urls'

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

WSGI_APPLICATION = 'garni_studenti.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db' / 'db.sqlite3',
    }
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}


LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Kiev'

USE_I18N = True
USE_L10N = True
USE_TZ = True


STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

AUTH_USER_MODEL = 'mainapp.customuser'
