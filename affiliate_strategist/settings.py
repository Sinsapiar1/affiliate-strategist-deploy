# config/settings.py - CONFIGURACIÓN PARA RAILWAY

import os
from pathlib import Path
from django.contrib.messages import constants as messages

# ✅ CONFIGURACIÓN BASE
BASE_DIR = Path(__file__).resolve().parent.parent

# ✅ SEGURIDAD - Variables de entorno
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-cambiar-en-produccion-12345')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# ✅ HOSTS PERMITIDOS - RAILWAY CONFIGURATION
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    '.railway.app',  # Permite cualquier subdominio de railway.app
    'web-production-6bf8c.up.railway.app',  # Tu dominio específico
]

# ✅ CSRF CONFIGURATION FOR RAILWAY
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://*.railway.app',  # Permite cualquier subdominio
    'https://web-production-6bf8c.up.railway.app',  # Tu dominio específico
]

# ✅ CONFIGURACIÓN ESPECÍFICA PARA RAILWAY
if os.environ.get('PRODUCTION'):
    # Railway maneja SSL automáticamente
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = False  # Railway ya maneja esto
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Configuración de archivos estáticos para Railway
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ✅ APLICACIONES
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

LOCAL_APPS = [
    'analyzer',
]

THIRD_PARTY_APPS = [
    # Agrega las apps que necesites
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_PARTY_APPS

# ✅ MIDDLEWARE - CON WHITENOISE PARA RAILWAY
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Para archivos estáticos en Railway
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# ✅ TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'analyzer' / 'templates',
        ],
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

WSGI_APPLICATION = 'config.wsgi.application'

# ✅ DATABASE - Usa Postgres si hay variables PG*/DATABASE_URL, si no, fallback a SQLite
if os.getenv('PGHOST') or os.getenv('DATABASE_URL') or os.getenv('DB_HOST'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('PGDATABASE', os.getenv('DB_NAME', 'railway')),
            'USER': os.getenv('PGUSER', os.getenv('DB_USER', 'postgres')),
            'PASSWORD': os.getenv('PGPASSWORD', os.getenv('DB_PASSWORD', '')),
            'HOST': os.getenv('PGHOST', os.getenv('DB_HOST', 'localhost')),
            'PORT': os.getenv('PGPORT', os.getenv('DB_PORT', '5432')),
            'OPTIONS': {
                'connect_timeout': 10,
            }
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': Path(__file__).resolve().parent.parent / 'db.sqlite3',
            'OPTIONS': {
                'timeout': 20,
            }
        }
    }

# ✅ Password validation
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

# ✅ Internationalization
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ✅ Static files configuration for Railway
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    BASE_DIR / 'static',
] if os.path.exists(BASE_DIR / 'static') else []

# ✅ Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ✅ CONFIGURACIÓN DE SESIONES
SESSION_COOKIE_AGE = 86400 * 7  # 7 días
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True

# ✅ CONFIGURACIÓN CSRF
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True

# ✅ CONFIGURACIÓN DE SEGURIDAD PARA PRODUCCIÓN
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# ✅ LOGGING
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
    },
}
