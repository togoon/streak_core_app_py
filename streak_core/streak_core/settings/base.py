import os
import json
from django.core.exceptions import ImproperlyConfigured
from corsheaders.defaults import default_headers
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration
import coreapp.middleware
"""
Django settings for streak_core project.

Generated by 'django-admin startproject' using Django 1.10.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
import json

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*lkajs!dsandlk#12-21jlaksd_l13129ljdlakj1912=93dlakd#klaasdds)1_-1l+1ksjai'

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True

# ALLOWED_HOSTS = [*]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'coreapp',
    'el_pagination',
    'corsheaders'
]

MIDDLEWARE = [
    'coreapp.middleware.CustomMiddlewareHeaderGenerator',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsPostCsrfMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'coreapp.middleware.CustomMiddleware'
]

ROOT_URLCONF = 'streak_core.urls'

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
                # 'django.core.context_processors.request',
            ],
        },
    },
]

TEMPLATE_CONTEXT_PROCESSORS = (
  'django.core.context_processors.request'
)

WSGI_APPLICATION = 'streak_core.wsgi.application'

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_HEADERS = default_headers + (
    'Access-Control-Allow-Credentials',
    'csrfmiddlewaretoken',
    'sessionid',
)
CORS_ORIGIN_WHITELIST = (
    'http://localhost:3000',
#    'http://10.10.50.96:3000'
    'https://streak-crypto.firebaseapp.com',
    'https://streaklab.com'
    )
# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_HEADERS = default_headers + (
    'Access-Control-Allow-Credentials',
    'csrfmiddlewaretoken',
    'sessionid',
)
CORS_ORIGIN_WHITELIST = (
    'http://localhost:3000',
#    'http://10.10.50.96:3000'
    'https://streak.zerodha.com',
    'https://streak.tech'
)

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'

# from configurations import Configuration

configs = None

try: 
	with open(os.environ.get('STREAK_CONFIG')) as f:
		configs = json.loads(f.read())
except:
	print 'Set the environment variable STREAK_CONFIG'
#	with open('../streak_core_app_config.json') as f:
#		configs = json.loads(f.read())

def get_env_var(setting, configs=configs):
 try:
	val = configs[setting]
	if val == 'True':
		val = True
	elif val == 'False':
		val = False
	return val
 except KeyError:
     error_msg = "ImproperlyConfigured: Set {0} environment variable".format(setting)
     raise ImproperlyConfigured(error_msg)

#get secret key
#SECRET_KEY = get_env_var("SECRET_KEY")

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': True,
#     'filters': {
#         'require_debug_false': {
#             '()': 'django.utils.log.RequireDebugFalse',
#         },
#         'require_debug_true': {
#             '()': 'django.utils.log.RequireDebugTrue',
#         },
#     },
#     'formatters': {
#         'simple': {
#             'format': '[%(asctime)s] %(levelname)s %(message)s',
#             'datefmt': '%Y-%m-%d %H:%M:%S'
#         },
#         'verbose': {
#             'format': '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
#             'datefmt': '%Y-%m-%d %H:%M:%S'
#         },
#     },
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'filters': ['require_debug_true'],
#             'class': 'logging.StreamHandler',
#             'formatter': 'simple'
#         },
#         'development_logfile': {
#             'level': 'DEBUG',
#             'filters': ['require_debug_true'],
#             'class': 'logging.FileHandler',
#             'filename': '/tmp/django_dev.log',
#             'formatter': 'verbose'
#         },
#         'production_logfile': {
#             'level': 'ERROR',
#             'filters': ['require_debug_false'],
#             'class': 'logging.handlers.RotatingFileHandler',
#             'filename': '/var/log/django/django_production.log',
#             'maxBytes' : 1024*1024*100, # 100MB
#             'backupCount' : 5,
#             'formatter': 'simple'
#         },
#         'dba_logfile': {
#             'level': 'DEBUG',
#             'filters': ['require_debug_false','require_debug_true'],
#             'class': 'logging.handlers.WatchedFileHandler',
#             'filename': '/var/log/dba/django_dba.log',
#             'formatter': 'simple'
#         },
#     },
#     'root': {
#         'level': 'DEBUG',
#         'handlers': ['console'],
#     },  
#     'loggers': {
#         'coffeehouse': {
#             'handlers': ['development_logfile','production_logfile'],
#          },
#         'dba': {
#             'handlers': ['dba_logfile'],
#         },
#         'django': {
#             'handlers': ['development_logfile','production_logfile'],
#         },
#         'py.warnings': {
#             'handlers': ['development_logfile'],
#         },
#     }
# }