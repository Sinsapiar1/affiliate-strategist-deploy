# analyzer/middleware.py - SOLUCIÓN DEFINITIVA QUE SÍ FUNCIONA

import logging
import time
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta
import hashlib
from django.core.cache import cache

logger = logging.getLogger(__name__)

class StrictRateLimitMiddleware:
    """
    Middleware ESTRICTO que SÍ bloquea usuarios anónimos
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # SOLO aplicar a análisis POST en home
        if request.path == '/' and request.method.upper() == 'POST':
            
            # VERIFICAR si es usuario anónimo
            if not request.user.is_authenticated:
                logger.warning(f"🚫 ANÓNIMO detectado: {self.get_client_ip(request)}")
                
                # BLOQUEAR INMEDIATAMENTE con límite estricto
                if not self.check_anonymous_strict_limit(request):
                    logger.error(f"🚫 BLOQUEANDO análisis anónimo: {self.get_client_ip(request)}")
                    return JsonResponse({
                        'success': False,
                        'limit_reached': True,
                        'error': '🚫 LÍMITE ALCANZADO: Solo 2 análisis gratuitos por día. ¡Regístrate para obtener 5 análisis mensuales!',
                        'register_url': '/register/',
                        'upgrade_url': '/upgrade/',
                        'message': 'Crea tu cuenta gratuita en 30 segundos y obtén acceso a más análisis.'
                    }, status=429)
                
                logger.info(f"✅ Permitiendo análisis anónimo: {self.get_client_ip(request)}")
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """Obtiene IP real considerando Railway"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip
    
    def check_anonymous_strict_limit(self, request):
        """
        Verificación ESTRICTA con múltiples layers
        """
        ip_address = self.get_client_ip(request)
        
        # LAYER 1: Base de datos (más confiable)
        db_allowed = self.check_db_limit(ip_address)
        if not db_allowed:
            return False
        
        # LAYER 2: Sesión como backup
        session_allowed = self.check_session_limit(request)
        if not session_allowed:
            return False
        
        return True
    
    def check_db_limit(self, ip_address):
        """Verificación por DB con transacciones atómicas"""
        try:
            from analyzer.models import AnonymousUsageTracker
            today = timezone.now().date()
            
            with transaction.atomic():
                tracker, created = AnonymousUsageTracker.objects.select_for_update().get_or_create(
                    ip_address=ip_address,
                    date=today,
                    defaults={'requests_count': 0}
                )
                
                logger.info(f"📊 DB Check - IP: {ip_address}, Count: {tracker.requests_count}")
                
                if tracker.requests_count >= 2:
                    logger.warning(f"🚫 DB LIMIT - IP {ip_address}: {tracker.requests_count}/2")
                    return False
                
                # Incrementar contador ANTES de permitir
                tracker.requests_count += 1
                tracker.save()
                
                logger.info(f"✅ DB ALLOW - IP {ip_address}: {tracker.requests_count}/2")
                return True
                
        except Exception as e:
            logger.error(f"❌ DB Error: {e}")
            return False  # Si falla DB, BLOQUEAR por seguridad
    
    def check_session_limit(self, request):
        """Verificación por sesión como backup"""
        try:
            day_key = timezone.now().strftime('%Y%m%d')
            session_key = f'anon_count_{day_key}'
            
            count = int(request.session.get(session_key, 0))
            logger.info(f"📊 Session Check: {count}/2")
            
            if count >= 2:
                logger.warning(f"🚫 SESSION LIMIT: {count}/2")
                return False
            
            # Incrementar sesión
            request.session[session_key] = count + 1
            request.session.modified = True
            
            logger.info(f"✅ SESSION ALLOW: {count + 1}/2")
            return True
            
        except Exception as e:
            logger.error(f"❌ Session Error: {e}")
            return False  # Si falla sesión, BLOQUEAR por seguridad


class UserCounterFixMiddleware:
    """
    Middleware para FIX del contador de usuarios registrados
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Solo resetear contador si es usuario autenticado
        if (hasattr(request, 'user') and 
            request.user.is_authenticated and 
            hasattr(request.user, 'profile')):
            
            try:
                # Reset mensual sin incrementar contador extra
                request.user.profile.reset_monthly_counter_if_needed()
            except Exception as e:
                logger.error(f"Error resetting counter: {e}")
        
        return self.get_response(request)


# Alias para compatibilidad
class ImprovedRateLimitMiddleware(StrictRateLimitMiddleware):
    pass

class RateLimitMiddleware(StrictRateLimitMiddleware):
    pass


# ========================================
# CLASES LEGACY PARA COMPATIBILIDAD
# ========================================

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