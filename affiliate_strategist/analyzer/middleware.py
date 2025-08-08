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
    """Middleware para rate limiting básico"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Solo aplicar rate limiting a análisis
        if request.path == '/' and request.method == 'POST':
            if not self.check_rate_limit(request):
                return JsonResponse({
                    'success': False,
                    'error': 'Demasiadas peticiones. Intenta en unos minutos.'
                }, status=429)
        
        return self.get_response(request)
    
    def check_rate_limit(self, request):
        """Verifica límites de peticiones"""
        ip = self.get_client_ip(request)
        user_key = f"rate_limit_{ip}"
        
        # Límite: 10 análisis por hora para IPs anónimas
        requests_count = cache.get(user_key, 0)
        
        if isinstance(request.user, AnonymousUser):
            limit = 10
        else:
            limit = 50  # Usuarios registrados tienen más límite
        
        if requests_count >= limit:
            return False
        
        # Incrementar contador
        cache.set(user_key, requests_count + 1, 3600)  # 1 hora
        return True
    
    def get_client_ip(self, request):
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