from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

DJANGO_ENV = os.getenv('DJANGO_ENV', 'development')
if DJANGO_ENV == 'production':
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.production')
else:
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.dev')

load_dotenv(dotenv_path)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-u3+-8octbnjgnqgve73pb2i_*d&_)5fpa=4nq4^oos1797((oe'

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'https://localhost:3000',
    'https://127.0.0.1:3000', 
    'http://localhost:8000',
    'https://localhost:8000',
]
CORS_ALLOW_CREDENTIALS = True
ALLOWED_HOSTS = ['*']
DEBUG=True

# Application definition
INSTALLED_APPS = [
    'django',
    'sustexcoporateapp',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drf_yasg',
    'corsheaders',
    'channels',
    'rest_framework',
    'usermanagement',
    'esganalyse',
    'chatbot',
    'benchmarking',
    'tasks'
]

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware', 
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
AUTH_USER_MODEL = "usermanagement.User"
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
ROOT_URLCONF = 'sustex_coporate.urls'

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

ASGI_APPLICATION = 'sustex_coporate.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': "sustex0",
        'CLIENT': {
            'host': "mongodb+srv://sustex0.2o8hscb.mongodb.net",
            'username': "sustexv0",
            'password': "sustexv0",
        }
    }
}

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

"""celery config settings"""

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
