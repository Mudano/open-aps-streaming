"""
Django settings for register project.
"""
import os
import boto3

# set up ssm client for config
ssm = boto3.client('ssm', region_name='eu-west-1')

def get_ssm_value(param_name):
    return ssm.get_parameter(Name = param_name)['Parameter']['Value']

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_ssm_value('openaps-register-django-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'register.apps.RegisterConfig',
    'openhumans'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'register.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'register', 'templates')],
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

WSGI_APPLICATION = 'register.wsgi.application'


# get postgres configuration from AWS SSM
POSTGRES_HOST = get_ssm_value('openaps-postgres-host')
POSTGRES_PORT = get_ssm_value('openaps-postgres-port')
POSTGRES_DB_NAME = get_ssm_value('aurora-db-name')
POSTGRES_USER = get_ssm_value('postgres-register-user')
POSTGRES_PASS = get_ssm_value('postgres-register-password')

postgres_connection_string =\
    f'postgresql://{POSTGRES_USER}:{POSTGRES_PASS}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB_NAME}'

OPENHUMANS_APP_BASE_URL = get_ssm_value('openaps-register-url')
APPLICATION_PORT = get_ssm_value('openaps-register-port')

OPENHUMANS_OH_BASE_URL = 'https://www.openhumans.org'
OPENHUMANS_PROJECT_ADDRESS = get_ssm_value('open-humans-project-address')
OPENHUMANS_CLIENT_ID = get_ssm_value('open-humans-client-id')
OPENHUMANS_CLIENT_SECRET = get_ssm_value('open-humans-client-secret')

LOGIN_REDIRECT_URL = '/'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'options': '-c search_path=register'
        },
        'NAME': POSTGRES_DB_NAME,
        'USER': POSTGRES_USER,
        'PASSWORD': POSTGRES_PASS,
        'HOST': POSTGRES_HOST,
        'PORT': POSTGRES_PORT,
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'register': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
        }
    },
}

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'register', 'static')
STATIC_URL = '/static/'
