from .base import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG')

ALLOWED_HOSTS = ['*']

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000"
]

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"http://localhost:3000",
]


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('NAME'),
        'USER': config('USER'),
        'PASSWORD': config('PASSWORD'),
        'HOST': config('HOST'),
        'PORT': config('PORT'),
    }
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'