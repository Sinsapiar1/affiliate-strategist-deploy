# analyzer/cache.py - SISTEMA DE CACHE INTELIGENTE

from django.core.cache import cache
from django.conf import settings
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
import hashlib
import json
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Gestor inteligente de cache para Affiliate Strategist"""
    
    # ✅ TIEMPOS DE CACHE POR TIPO
    CACHE_TIMEOUTS = {
        'analysis_result': 86400,      # 24 horas
        'product_info': 3600,          # 1 hora
        'user_stats': 1800,            # 30 minutos
        'platform_stats': 7200,       # 2 horas
        'templates': 21600,            # 6 horas
        'similar_analysis': 43200,     # 12 horas
    }
    
    # ✅ PREFIJOS PARA ORGANIZAR KEYS
    CACHE_PREFIXES = {
        'analysis': 'analysis',
        'user': 'user',
        'product': 'product',
        'stats': 'stats',
        'template': 'template',
        'search': 'search',
    }
    
    @classmethod
    def get_cache_key(cls, prefix, identifier, **kwargs):
        """Genera clave de cache consistente"""
        # Crear string único basado en parámetros
        key_parts = [prefix, str(identifier)]
        
        if kwargs:
            # Ordenar kwargs para consistencia
            sorted_kwargs = sorted(kwargs.items())
            params_str = json.dumps(sorted_kwargs, sort_keys=True)
            key_parts.append(hashlib.md5(params_str.encode()).hexdigest()[:8])
        
        return ':'.join(key_parts)
    
    @classmethod
    def cache_analysis_result(cls, analysis_params, result):
        """Cachea resultado de análisis para evitar duplicados"""
        # Crear hash único de los parámetros de análisis
        cache_key = cls._generate_analysis_hash(analysis_params)
        full_key = cls.get_cache_key('analysis', cache_key)
        
        cache_data = {
            'result': result,
            'cached_at': timezone.now().isoformat(),
            'params': analysis_params
        }
        
        cache.set(
            full_key, 
            cache_data, 
            cls.CACHE_TIMEOUTS['analysis_result']
        )
        
        logger.info(f"🔄 Cached analysis result: {full_key}")
        return full_key
    
    @classmethod
    def get_cached_analysis(cls, analysis_params):
        """Busca análisis similar en cache"""
        cache_key = cls._generate_analysis_hash(analysis_params)
        full_key = cls.get_cache_key('analysis', cache_key)
        
        cached_data = cache.get(full_key)
        if cached_data:
            logger.info(f"✅ Cache hit for analysis: {full_key}")
            return cached_data
        
        return None
    
    @classmethod
    def _generate_analysis_hash(cls, params):
        """Genera hash único para parámetros de análisis"""
        # Extraer parámetros clave que definen un análisis único
        key_params = {
            'product_url': params.get('product_url', ''),
            'platform': params.get('platform', ''),
            'target_audience': params.get('target_audience', ''),
            'analysis_type': params.get('analysis_type', 'basic'),
            'campaign_goal': params.get('campaign_goal', ''),
            'tone': params.get('tone', ''),
        }
        
        # Crear hash MD5 de los parámetros clave
        params_str = json.dumps(key_params, sort_keys=True)
        return hashlib.md5(params_str.encode()).hexdigest()
    
    @classmethod
    def cache_product_info(cls, url, product_data):
        """Cachea información de producto"""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        cache_key = cls.get_cache_key('product', url_hash)
        
        cache.set(
            cache_key,
            product_data,
            cls.CACHE_TIMEOUTS['product_info']
        )
        
        logger.info(f"🔄 Cached product info: {url}")
        return cache_key
    
    @classmethod
    def get_cached_product_info(cls, url):
        """Obtiene información de producto del cache"""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        cache_key = cls.get_cache_key('product', url_hash)
        
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"✅ Cache hit for product: {url}")
        
        return cached_data
    
    @classmethod
    def cache_user_stats(cls, user_id, stats_data):
        """Cachea estadísticas de usuario"""
        cache_key = cls.get_cache_key('user_stats', user_id)
        
        cache.set(
            cache_key,
            stats_data,
            cls.CACHE_TIMEOUTS['user_stats']
        )
        
        return cache_key
    
    @classmethod
    def get_cached_user_stats(cls, user_id):
        """Obtiene estadísticas de usuario del cache"""
        cache_key = cls.get_cache_key('user_stats', user_id)
        return cache.get(cache_key)
    
    @classmethod
    def invalidate_user_cache(cls, user_id):
        """Invalida cache relacionado con usuario"""
        patterns = [
            cls.get_cache_key('user_stats', user_id),
            cls.get_cache_key('user', f"{user_id}_*"),
        ]
        
        for pattern in patterns:
            cache.delete(pattern)
        
        logger.info(f"🗑️ Invalidated cache for user: {user_id}")
    
    @classmethod
    def cache_platform_stats(cls, stats_data):
        """Cachea estadísticas generales de plataformas"""
        cache_key = cls.get_cache_key('stats', 'platforms')
        
        cache.set(
            cache_key,
            stats_data,
            cls.CACHE_TIMEOUTS['platform_stats']
        )
        
        return cache_key
    
    @classmethod
    def get_cached_platform_stats(cls):
        """Obtiene estadísticas de plataformas del cache"""
        cache_key = cls.get_cache_key('stats', 'platforms')
        return cache.get(cache_key)
    
    @classmethod
    def cache_templates(cls, platform, templates_data):
        """Cachea plantillas por plataforma"""
        cache_key = cls.get_cache_key('template', platform)
        
        cache.set(
            cache_key,
            templates_data,
            cls.CACHE_TIMEOUTS['templates']
        )
        
        return cache_key
    
    @classmethod
    def get_cached_templates(cls, platform):
        """Obtiene plantillas del cache"""
        cache_key = cls.get_cache_key('template', platform)
        return cache.get(cache_key)
    
    @classmethod
    def warm_cache(cls):
        """Precarga cache con datos frecuentemente usados"""
        logger.info("🔥 Warming up cache...")
        
        try:
            # Precargar estadísticas de plataformas
            from .models import AnalysisHistory
            platform_stats = AnalysisHistory.objects.filter(
                success=True
            ).values('platform').annotate(
                count=Count('id')
            ).order_by('-count')[:10]
            
            cls.cache_platform_stats(list(platform_stats))
            
            # Precargar plantillas populares
            from .models import MarketingTemplate
            for platform_choice in AnalysisHistory.PLATFORM_CHOICES:
                platform = platform_choice[0]
                templates = MarketingTemplate.objects.filter(
                    platform=platform,
                    is_active=True
                ).order_by('-success_rate')[:10]
                
                cls.cache_templates(platform, list(templates.values()))
            
            logger.info("✅ Cache warmed successfully")
            
        except Exception as e:
            logger.error(f"❌ Error warming cache: {str(e)}")
    
    @classmethod
    def clear_all_cache(cls):
        """Limpia todo el cache de la aplicación"""
        cache.clear()
        logger.warning("🗑️ All cache cleared")
    
    @classmethod
    def get_cache_stats(cls):
        """Obtiene estadísticas del cache"""
        # Esta función depende del backend de cache usado
        try:
            # Para memcached o redis
            if hasattr(cache, '_cache'):
                if hasattr(cache._cache, 'get_stats'):
                    return cache._cache.get_stats()
            
            # Estadísticas básicas simuladas
            return {
                'status': 'active',
                'backend': str(cache.__class__),
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {'status': 'error', 'error': str(e)}


# ✅ DECORADORES PARA CACHE AUTOMÁTICO
from functools import wraps

def cache_result(timeout=None, key_prefix='auto'):
    """Decorador para cachear resultados de funciones"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generar clave única basada en función y argumentos
            func_name = f"{func.__module__}.{func.__name__}"
            args_str = str(args) + str(sorted(kwargs.items()))
            cache_key = f"{key_prefix}:{func_name}:{hashlib.md5(args_str.encode()).hexdigest()[:12]}"
            
            # Intentar obtener del cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"📋 Cache hit: {cache_key}")
                return cached_result
            
            # Ejecutar función y cachear resultado
            result = func(*args, **kwargs)
            
            cache_timeout = timeout or 3600  # 1 hora por defecto
            cache.set(cache_key, result, cache_timeout)
            
            logger.debug(f"💾 Cached result: {cache_key}")
            return result
        
        return wrapper
    return decorator

def invalidate_cache_on_save(cache_pattern):
    """Decorador para invalidar cache cuando se guarda un modelo"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            
            # Invalidar cache relacionado
            if hasattr(self, 'pk') and self.pk:
                cache_key = cache_pattern.format(pk=self.pk)
                cache.delete(cache_key)
                logger.debug(f"🗑️ Invalidated cache: {cache_key}")
            
            return result
        return wrapper
    return decorator


# ✅ IMPLEMENTACIÓN EN UTILS DE SCRAPING
def cached_scrape_product_info(url):
    """Versión con cache del scraping de productos"""
    # Buscar en cache primero
    cached_data = CacheManager.get_cached_product_info(url)
    if cached_data:
        return cached_data
    
    # Si no está en cache, hacer scraping
    from .utils.scraping import scrape_product_info
    result = scrape_product_info(url)
    
    # Cachear solo si es exitoso
    if result.get('success'):
        CacheManager.cache_product_info(url, result)
    
    return result


# ✅ IMPLEMENTACIÓN EN VISTAS CON CACHE
class CachedViewMixin:
    """Mixin para agregar funcionalidad de cache a vistas"""
    
    cache_timeout = 300  # 5 minutos por defecto
    cache_key_prefix = 'view'
    
    def get_cache_key(self, request):
        """Genera clave de cache para la vista"""
        key_parts = [
            self.cache_key_prefix,
            self.__class__.__name__,
            request.path,
            str(sorted(request.GET.items())),
        ]
        
        if request.user.is_authenticated:
            key_parts.append(f"user_{request.user.id}")
        
        key_str = ':'.join(key_parts)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get_cached_response(self, request):
        """Busca respuesta en cache"""
        cache_key = self.get_cache_key(request)
        return cache.get(cache_key)
    
    def cache_response(self, request, response):
        """Cachea respuesta"""
        cache_key = self.get_cache_key(request)
        cache.set(cache_key, response, self.cache_timeout)
        return response


# ✅ COMANDO DE GESTIÓN PARA CACHE
"""
# analyzer/management/commands/manage_cache.py

from django.core.management.base import BaseCommand
from analyzer.cache import CacheManager

class Command(BaseCommand):
    help = 'Gestiona el sistema de cache'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['warm', 'clear', 'stats'],
            help='Acción a realizar'
        )
    
    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'warm':
            CacheManager.warm_cache()
            self.stdout.write(self.style.SUCCESS('✅ Cache warmed'))
        
        elif action == 'clear':
            CacheManager.clear_all_cache()
            self.stdout.write(self.style.WARNING('🗑️ Cache cleared'))
        
        elif action == 'stats':
            stats = CacheManager.get_cache_stats()
            self.stdout.write(f"📊 Cache stats: {stats}")
"""


# ✅ MIDDLEWARE DE CACHE INTELIGENTE
class SmartCacheMiddleware:
    """Middleware para cache inteligente de respuestas"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Solo cachear GET requests para usuarios anónimos en ciertas URLs
        if (request.method == 'GET' and 
            not request.user.is_authenticated and 
            self.should_cache_request(request)):
            
            # Buscar en cache
            cache_key = self.get_request_cache_key(request)
            cached_response = cache.get(cache_key)
            
            if cached_response:
                logger.debug(f"📋 Served from cache: {request.path}")
                return cached_response
        
        response = self.get_response(request)
        
        # Cachear respuesta si es apropiado
        if (response.status_code == 200 and 
            request.method == 'GET' and 
            not request.user.is_authenticated and
            self.should_cache_request(request)):
            
            cache_key = self.get_request_cache_key(request)
            cache.set(cache_key, response, 300)  # 5 minutos
        
        return response
    
    def should_cache_request(self, request):
        """Determina si debe cachear la request"""
        cacheable_paths = [
            '/public-history/',
            '/upgrade/',
        ]
        
        return any(request.path.startswith(path) for path in cacheable_paths)
    
    def get_request_cache_key(self, request):
        """Genera clave de cache para request"""
        key_parts = [
            'middleware',
            request.path,
            str(sorted(request.GET.items()))
        ]
        
        key_str = ':'.join(key_parts)
        return hashlib.md5(key_str.encode()).hexdigest()