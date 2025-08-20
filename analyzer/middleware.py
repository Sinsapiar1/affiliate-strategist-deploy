# analyzer/middleware.py - MIDDLEWARE PERSONALIZADO

import time
import logging
from django.http import JsonResponse
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

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


class RateLimitMiddleware:
    """Middleware para rate limiting robusto"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        import logging
        logger = logging.getLogger(__name__)
        
        # Solo aplicar a análisis POST en home
        if request.path == '/' and request.method == 'POST':
            # Verificar si es usuario anónimo
            if not getattr(request, 'user', None) or not request.user.is_authenticated:
                ip_address = self.get_client_ip(request)
                logger.info(f"🔍 Verificando rate limit para IP anónima: {ip_address}")
                
                # Usar el modelo para verificar límites
                try:
                    from analyzer.models import AnonymousUsageTracker
                    
                    if not AnonymousUsageTracker.can_make_request(ip_address, limit=2):
                        logger.warning(f"🚫 Rate limit exceeded for IP: {ip_address}")
                        return JsonResponse({
                            'success': False,
                            'limit_reached': True,
                            'error': 'Has alcanzado el límite diario de análisis gratuitos (2). Crea una cuenta para más.',
                            'register_url': '/register/'
                        }, status=429)
                    
                    logger.info(f"✅ Rate limit OK para IP: {ip_address}")
                    
                except Exception as e:
                    logger.error(f"❌ Error en rate limiting: {e}")
                    # En caso de error, permitir la request
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """Obtiene la IP real del cliente (Railway/proxy aware)"""
        # Railway usa X-Forwarded-For
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
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
    
    # analyzer/middleware.py - AGREGAR esta clase (no reemplazar las existentes)

class UserLimitsMiddleware:
    """Middleware para verificar y actualizar límites de usuario"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Reset contador mensual si es necesario
        if hasattr(request, 'user') and request.user.is_authenticated:
            if hasattr(request.user, 'profile'):
                request.user.profile.reset_monthly_counter_if_needed()
        
        response = self.get_response(request)
        return response