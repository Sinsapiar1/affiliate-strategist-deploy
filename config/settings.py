# config/settings.py - CONFIGURACIÓN MEJORADA Y SEGURA

import os
from pathlib import Path
from django.contrib.messages import constants as messages

# ✅ CONFIGURACIÓN BASE
BASE_DIR = Path(__file__).resolve().parent.parent

# ✅ SEGURIDAD - Variables de entorno recomendadas
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-cambiar-en-produccion-12345')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# ✅ HOSTS PERMITIDOS
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    '.railway.app',  # Permite subdominios de Railway en producción
]

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
    'analyzer.apps.AnalyzerConfig',
]

THIRD_PARTY_APPS = [
    # 'rest_framework',  # Para APIs futuras
    # 'corsheaders',     # Para CORS si necesitas
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_PARTY_APPS

# ✅ MIDDLEWARE MEJORADO
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # Rate limit debe ir después de Authentication para distinguir usuario anónimo vs autenticado
    'analyzer.middleware.RateLimitMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'analyzer.middleware.UserLimitsMiddleware',
    # 'corsheaders.middleware.CorsMiddleware',  # Si necesitas CORS
]

ROOT_URLCONF = 'config.urls'

# ✅ TEMPLATES MEJORADOS
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',  # Templates globales
            BASE_DIR / 'analyzer' / 'templates',  # Templates específicos
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # 'analyzer.context_processors.global_context',  # Context processor personalizado
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ✅ BASE DE DATOS: Postgres si hay variables, si no, SQLite
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
            'NAME': BASE_DIR / 'db.sqlite3',
            'OPTIONS': {
                'timeout': 20,  # Timeout en segundos
            }
        }
    }

# ✅ VALIDACIÓN DE CONTRASEÑAS
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,  # Mínimo 6 caracteres
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ✅ INTERNACIONALIZACIÓN
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Mexico_City'  # Cambiar según tu ubicación
USE_I18N = True
USE_TZ = True

# ✅ ARCHIVOS ESTÁTICOS Y MEDIA
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
] if os.path.exists(BASE_DIR / 'static') else []

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# WhiteNoise storage para archivos estáticos comprimidos y cacheados
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ✅ CONFIGURACIÓN DE ARCHIVOS
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ✅ CONFIGURACIÓN DE MENSAJES
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',  # Bootstrap usa 'danger' en lugar de 'error'
}

# ✅ CONFIGURACIÓN DE SESIONES
SESSION_COOKIE_AGE = 86400 * 7  # 7 días
SESSION_COOKIE_SECURE = not DEBUG  # HTTPS en producción
SESSION_COOKIE_HTTPONLY = True
SESSION_SAVE_EVERY_REQUEST = True

# ✅ CONFIGURACIÓN CSRF
CSRF_COOKIE_SECURE = not DEBUG  # HTTPS en producción
CSRF_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://*.railway.app',  # Confianza para dominios de Railway en HTTPS
]

# ✅ DETRÁS DE PROXY (Railway)
# Asegura que Django reconozca correctamente las peticiones HTTPS detrás del proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# Railway ya maneja el redireccionamiento a HTTPS
SECURE_SSL_REDIRECT = False

# ✅ CONFIGURACIÓN DE SEGURIDAD
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = 'DENY'

# ✅ LOGGING MEJORADO
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
        'analyzer': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

# ✅ CREAR DIRECTORIO DE LOGS y CACHE
os.makedirs(BASE_DIR / 'logs', exist_ok=True)
os.makedirs(BASE_DIR / 'cache', exist_ok=True)

# ✅ CONFIGURACIÓN DE EMAIL (para futuras notificaciones)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' if DEBUG else 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ✅ CONFIGURACIÓN DE CACHE MEJORADA CON REDIS
# Esta configuración resuelve el problema P2 de rate limiting

# Detectar si Railway tiene Redis configurado
REDIS_URL = os.getenv('REDIS_URL') or os.getenv('REDISCLOUD_URL') or os.getenv('REDIS_PRIVATE_URL')

if REDIS_URL:
    # ✅ REDIS DISPONIBLE - Configuración para producción
    print("🔗 Redis detectado, usando cache compartido")
    
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'socket_timeout': 5,
                'socket_connect_timeout': 5,
                'connection_pool_kwargs': {
                    'max_connections': 20,
                    'socket_keepalive': True,
                    'socket_keepalive_options': {},
                },
                'compressor': 'django.core.cache.backends.redis.CompressionMiddleware',
            },
            'KEY_PREFIX': 'affiliate_strategist',
            'TIMEOUT': 300,  # 5 minutos por defecto
        }
    }
    
    # ✅ CONFIGURACIÓN DE SESIONES EN REDIS (opcional, mejora rendimiento)
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
    
else:
    # ✅ FALLBACK SIN REDIS - Para desarrollo local
    print("⚠️ Redis no disponible, usando cache local")
    
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': str(BASE_DIR / 'cache'),
            'TIMEOUT': 300,
            'OPTIONS': {
                'MAX_ENTRIES': 10000,
            }
        }
    }

# ✅ CONFIGURACIÓN PERSONALIZADA DE LA APP
AFFILIATE_STRATEGIST_SETTINGS = {
    'MAX_ANALYSES_PER_DAY': 50,  # Límite diario para usuarios gratuitos
    'AI_TIMEOUT_SECONDS': 60,   # Timeout para llamadas de IA
    'SCRAPING_TIMEOUT_SECONDS': 30,  # Timeout para scraping
    'MAX_COMPETITORS': 5,        # Máximo competidores en análisis
    'CACHE_ANALYSIS_HOURS': 24,  # Horas para cachear análisis similares
}

# ✅ CONFIGURACIÓN DE DESARROLLO
if DEBUG:
    # Herramientas de desarrollo
    try:
        import debug_toolbar
        INSTALLED_APPS.append('debug_toolbar')
        MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
        INTERNAL_IPS = ['127.0.0.1', 'localhost']
    except ImportError:
        pass
    
    # Configuración relajada para desarrollo
    ALLOWED_HOSTS = ['*']
    
    # Email a consola en desarrollo
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ✅ CONFIGURACIÓN DE LOGGING MEJORADA PARA DEBUGGING
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'rate_limit_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'rate_limit.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
        'analyzer': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'analyzer.middleware': {
            'handlers': ['rate_limit_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# ✅ CREAR DIRECTORIOS NECESARIOS
os.makedirs(BASE_DIR / 'logs', exist_ok=True)
os.makedirs(BASE_DIR / 'cache', exist_ok=True)