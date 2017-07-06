"""
Django settings for django_mongoengine_restful project.

Generated by 'django-admin startproject' using Django 1.11.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import sys
import mongoengine

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'c*s4n%@c#3sjzc(g4fiq7htu0pfu2reuk)ax((c7y-^h^cu+$*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_mongoengine',
    'entity',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

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

WSGI_APPLICATION = 'project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        # 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        # 'ENGINE': '',
    }
}


def is_test():
    """
    Checks, if we're running the server for real or in unit-test.

    We might need a better implementation of this function.
    """
    if 'test' in sys.argv or 'testserver' in sys.argv:
        return True
    else:
        return False

# MongoEngine
# https://github.com/MongoEngine/mongoengine
if not is_test():
    _MONGODB_USER = 'admin'
    _MONGODB_PASSWD = 'password'
    _MONGODB_HOST = 'localhost:27017'
    _MONGODB_NAME = 'django'
    _MONGODB_DATABASE_HOST = \
        'mongodb://%s:%s@%s/%s' \
        % (_MONGODB_USER, _MONGODB_PASSWD, _MONGODB_HOST, _MONGODB_NAME)

    mongoengine.connect(db=_MONGODB_NAME, host=_MONGODB_DATABASE_HOST)
else:
    _MONGODB_USER = 'admin'
    _MONGODB_PASSWD = 'password'
    _MONGODB_HOST = 'localhost:27017'
    _MONGODB_NAME = 'django_test'
    _MONGODB_DATABASE_HOST = \
        'mongodb://%s:%s@%s/%s' \
        % (_MONGODB_USER, _MONGODB_PASSWD, _MONGODB_HOST, _MONGODB_NAME)

    mongoengine.connect(db=_MONGODB_NAME, host=_MONGODB_DATABASE_HOST)
    

# This doesn't seem to work with the current version of mongoengine. Just using
# the default authentication for now
AUTHENTICATION_BACKENDS = (
     'mongoengine.django.auth.MongoEngineBackend',
)


# SESSION_ENGINE = 'mongoengine.django.sessions'

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'


# So that you can see stdout while testing
NOSE_ARGS = ['--nocapture',
             '--nologcapture',]
