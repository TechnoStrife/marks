"""
Django settings for marks project.
"""
import json
import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


def path_from_project_root(path: str):
    return os.path.join(BASE_DIR, path)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

db_credentials_file = os.path.join(BASE_DIR, 'db_credentials.json')

DEBUG = not os.path.exists(db_credentials_file)

MAX_RUN_TIME = 60 * 60  # 1 hour

if not DEBUG:
    sentry_sdk.init(
        dsn="https://d3a95295847a413187364e8cce4f84e3@sentry.io/1828383",
        integrations=[DjangoIntegration()],
        environment="Debug" if DEBUG else "Production"
    )


REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100
}


# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

SECRET_KEY = 'y&5h#2ovxoyndpw8u@q4^-uc5gf(1623fx3f43u81yqi5z%%1x'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # 'webpack_loader',
    'background_task',
    'rest_framework',
    'django.contrib.staticfiles',
    'main',
    'main.summary',
    'frontend',
    'api',
    'dnevnik'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'livereload.middleware.LiveReloadScript',
]

ROOT_URLCONF = 'marks.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'marks.wsgi.application'

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
    ALLOWED_HOSTS = ['*']
else:
    db_credentials = json.load(open(db_credentials_file, 'r'))
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            **db_credentials['db'],
            'HOST': '127.0.0.1',
            'PORT': '3306',
            'OPTIONS': {
                'init_command': 'SET default_storage_engine=INNODB,'
                                'character_set_connection=utf8,'
                                'collation_connection=utf8_unicode_ci '
            }
        }
    }
    ALLOWED_HOSTS = [db_credentials['host']]


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


LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True
USE_TZ = True


STATIC_URL = '/static/'
STATIC_ROOT = path_from_project_root('static')
STATICFILES_DIRS = [
    # path_from_project_root('static'),
    path_from_project_root('dist')
]

