# analyzer/middleware.py - VERSIÓN MEJORADA PARA RESOLVER RATE LIMITING

import time
import logging
from django.http import JsonResponse
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from datetime import datetime, timedelta
import hashlib
import json

logger = logging.getLogger(__name__)

class ImprovedRateLimitMiddleware:
    """
    Middleware mejorado para rate limiting que funciona tanto 
    con Redis como con fallbacks locales
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Solo aplicar a análisis POST en home
        if request.path == '/' and request.method.upper() == 'POST':
            logger.info(f"🎯 RATE LIMIT: Verificando {request.method} {request.path}")
            
            # Verificar si es usuario anónimo
            if not request.user.is_authenticated:
                logger.info("🚫 RATE LIMIT: Usuario anónimo detectado")
                
                # Obtener IP real
                ip_address = self.get_real_client_ip(request)
                logger.info(f"🔍 RATE LIMIT: IP detectada: {ip_address}")
                
                # Verificar límite con estrategia multi-layer
                can_proceed = self.check_anonymous_limit(ip_address, request)
                
                if not can_proceed:
                    logger.warning(f"🚫 RATE LIMIT: BLOQUEANDO IP {ip_address}")
                    return JsonResponse({
                        'success': False,
                        'limit_reached': True,
                        'error': 'Has alcanzado el límite diario de análisis gratuitos (2). Crea una cuenta para más análisis.',
                        'register_url': '/register/',
                        'reset_in_hours': self.get_hours_until_reset()
                    }, status=429)
                
                logger.info(f"✅ RATE LIMIT: PERMITIENDO IP {ip_address}")
        
        response = self.get_response(request)
        return response
    
    def get_real_client_ip(self, request):
        """
        Obtiene la IP real del cliente considerando proxies de Railway
        """
        # Railway y otros proxies usan estos headers
        possible_headers = [
            'HTTP_CF_CONNECTING_IP',      # Cloudflare
            'HTTP_X_FORWARDED_FOR',       # Estándar
            'HTTP_X_REAL_IP',             # Nginx
            'HTTP_X_CLIENT_IP',           # Apache
            'REMOTE_ADDR'                 # Fallback
        ]
        
        for header in possible_headers:
            ip = request.META.get(header)
            if ip:
                # X-Forwarded-For puede tener múltiples IPs
                if ',' in ip:
                    ip = ip.split(',')[0].strip()
                
                # Validar que es una IP válida
                if self.is_valid_ip(ip):
                    logger.debug(f"🔍 IP encontrada en {header}: {ip}")
                    return ip
        
        # Fallback
        return '127.0.0.1'
    
    def is_valid_ip(self, ip):
        """Validación básica de IP"""
        import re
        pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
        return pattern.match(ip) and all(0 <= int(x) <= 255 for x in ip.split('.'))
    
    def check_anonymous_limit(self, ip_address, request):
        """
        Estrategia multi-layer para verificar límites:
        1. Cache (Redis si disponible)
        2. Base de datos
        3. Sesión (fallback)
        """
        
        # LAYER 1: Cache (Redis o local)
        cache_result = self.check_cache_limit(ip_address)
        if cache_result is not None:
            return cache_result
        
        # LAYER 2: Base de datos (más confiable)
        db_result = self.check_database_limit(ip_address)
        if db_result is not None:
            return db_result
        
        # LAYER 3: Sesión (último recurso)
        return self.check_session_limit(request)
    
    def check_cache_limit(self, ip_address):
        """Verificación por cache con operaciones atómicas"""
        try:
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            cache_key = f'anon_limit:{ip_address}:{today}'
            
            # Usar add() para operación atómica si el cache lo soporta
            if hasattr(cache, 'add'):
                # Intentar crear la entrada con valor 1
                if cache.add(cache_key, 1, 86400):  # 24 horas
                    logger.info(f"📦 CACHE: Primera request del día para {ip_address}")
                    return True
                
                # Si ya existe, intentar incrementar
                try:
                    current_count = cache.get(cache_key, 0)
                    if current_count >= 2:
                        logger.warning(f"📦 CACHE: Límite alcanzado para {ip_address}: {current_count}")
                        return False
                    
                    # Incrementar de forma "pseudo-atómica"
                    if hasattr(cache, 'incr'):
                        new_count = cache.incr(cache_key)
                        logger.info(f"📦 CACHE: Incrementado para {ip_address}: {new_count}")
                        return new_count <= 2
                    else:
                        # Fallback sin atomicidad garantizada
                        cache.set(cache_key, current_count + 1, 86400)
                        return True
                        
                except Exception as e:
                    logger.warning(f"📦 CACHE: Error en incr: {e}")
                    return None
            else:
                logger.warning("📦 CACHE: Backend no soporta add(), usando DB")
                return None
                
        except Exception as e:
            logger.error(f"📦 CACHE: Error general: {e}")
            return None
    
    def check_database_limit(self, ip_address):
        """Verificación por base de datos con locking"""
        try:
            from analyzer.models import AnonymousUsageTracker
            from django.utils import timezone
            from django.db import transaction
            
            today = timezone.now().date()
            
            with transaction.atomic():
                # Usar select_for_update para evitar race conditions
                tracker, created = AnonymousUsageTracker.objects.select_for_update().get_or_create(
                    ip_address=ip_address,
                    date=today,
                    defaults={'requests_count': 0}
                )
                
                if tracker.requests_count >= 2:
                    logger.warning(f"💾 DB: Límite alcanzado para {ip_address}: {tracker.requests_count}")
                    return False
                
                # Incrementar contador
                tracker.requests_count += 1
                tracker.save()
                
                logger.info(f"💾 DB: Incrementado para {ip_address}: {tracker.requests_count}")
                return True
                
        except Exception as e:
            logger.error(f"💾 DB: Error en database limit: {e}")
            return None
    
    def check_session_limit(self, request):
        """Verificación por sesión como último recurso"""
        try:
            from django.utils import timezone
            day_key = timezone.now().strftime('%Y%m%d')
            sess_key = f'anon_requests_{day_key}'
            
            count = int(request.session.get(sess_key, 0))
            
            if count >= 2:
                logger.warning(f"🗃️ SESSION: Límite alcanzado: {count}")
                return False
            
            request.session[sess_key] = count + 1
            request.session.modified = True
            
            logger.info(f"🗃️ SESSION: Incrementado: {count + 1}")
            return True
            
        except Exception as e:
            logger.error(f"🗃️ SESSION: Error: {e}")
            # En caso de error total, permitir (fail-open)
            return True
    
    def get_hours_until_reset(self):
        """Calcula horas hasta el reset del día siguiente"""
        from datetime import datetime, timedelta
        now = datetime.now()
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        delta = tomorrow - now
        return round(delta.total_seconds() / 3600, 1)


class UserLimitsMiddleware:
    """Middleware para verificar límites de usuarios autenticados"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Reset contador mensual si es necesario para usuarios autenticados
        if hasattr(request, 'user') and request.user.is_authenticated:
            if hasattr(request.user, 'profile'):
                try:
                    request.user.profile.reset_monthly_counter_if_needed()
                except Exception as e:
                    logger.error(f"Error resetting monthly counter: {e}")
        
        return self.get_response(request)


# ========================================
# CLASES LEGACY PARA COMPATIBILIDAD
# ========================================

class RateLimitMiddleware(ImprovedRateLimitMiddleware):
    """Alias para compatibilidad con configuración existente"""
    pass


class RequestLoggingMiddleware:
    """Middleware para logging detallado de requests"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        
        # Log del request entrante
        logger.info(f"📥 {request.method} {request.path} from {self.get_client_ip(request)}")
        
        response = self.get_response(request)
        
        # Log del response
        duration = time.time() - start_time
        logger.info(f"📤 {request.method} {request.path} - {response.status_code} ({duration:.2f}s)")
        
        return response
    
    def get_client_ip(self, request):
        """Obtiene la IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware:
    """Middleware para headers de seguridad"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Headers de seguridad
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # CSP básico
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "font-src 'self' cdnjs.cloudflare.com;"
        )
        
        return response


class UserActivityMiddleware:
    """Middleware para trackear actividad de usuarios"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Actualizar última actividad para usuarios autenticados
        if hasattr(request, 'user') and request.user.is_authenticated:
            self.update_user_activity(request.user)
        
        return response
    
    def update_user_activity(self, user):
        """Actualiza la última actividad del usuario"""
        try:
            user.last_login = datetime.now()
            user.save(update_fields=['last_login'])
        except:
            pass  # No fallar si hay error


class MaintenanceModeMiddleware:
    """Middleware para modo de mantenimiento"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Verificar si está en modo mantenimiento
        maintenance_mode = cache.get('maintenance_mode', False)
        
        if maintenance_mode and not request.user.is_superuser:
            from django.shortcuts import render
            return render(request, 'analyzer/maintenance.html', status=503)
        
        return self.get_response(request)