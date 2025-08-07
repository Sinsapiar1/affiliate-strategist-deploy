# analyzer/views_auth.py
# NUEVO ARCHIVO - Sistema de autenticación

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.http import JsonResponse
from django.db import transaction
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import json
import re

class RegisterView(View):
    """
    Registro de nuevos usuarios con validación inteligente
    """
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'analyzer/auth/register.html')
    
    def post(self, request):
        try:
            # Obtener datos
            data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
            
            username = data.get('username', '').strip()
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            password2 = data.get('password2', '')
            company = data.get('company_name', '').strip()
            invitation_code = data.get('invitation_code', '').strip()
            
            # Validaciones
            errors = self.validate_registration(username, email, password, password2)
            if errors:
                return JsonResponse({'success': False, 'errors': errors}, status=400)
            
            # Crear usuario con transacción
            with transaction.atomic():
                # Crear usuario
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                
                # Actualizar perfil
                user.profile.company_name = company
                
                # Si tiene código de invitación, dar beneficios
                if invitation_code:
                    self.process_invitation(invitation_code, user)
                
                user.profile.save()
                
                # Auto-login después del registro
                login(request, user)
                
                # Log de uso
                UsageLog.objects.create(
                    user=user,
                    action='user_registered',
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                return JsonResponse({
                    'success': True,
                    'message': '¡Bienvenido a Affiliate Strategist Pro!',
                    'redirect': '/',
                    'user': {
                        'username': user.username,
                        'plan': user.profile.get_plan_display(),
                        'analyses_remaining': user.profile.analyses_limit_monthly
                    }
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Error al crear cuenta. Intenta nuevamente.'
            }, status=500)
    
    def validate_registration(self, username, email, password, password2):
        """Validación completa de registro"""
        errors = {}
        
        # Username
        if not username or len(username) < 3:
            errors['username'] = 'El nombre de usuario debe tener al menos 3 caracteres'
        elif not re.match(r'^[\w.@+-]+$', username):
            errors['username'] = 'Nombre de usuario inválido. Solo letras, números y @/./+/-/_'
        elif User.objects.filter(username=username).exists():
            errors['username'] = 'Este nombre de usuario ya está registrado'
        
        # Email
        try:
            validate_email(email)
            if User.objects.filter(email=email).exists():
                errors['email'] = 'Este email ya está registrado'
        except ValidationError:
            errors['email'] = 'Email inválido'
        
        # Password
        if len(password) < 8:
            errors['password'] = 'La contraseña debe tener al menos 8 caracteres'
        elif not re.search(r'[A-Za-z]', password) or not re.search(r'[0-9]', password):
            errors['password'] = 'La contraseña debe contener letras y números'
        elif password != password2:
            errors['password2'] = 'Las contraseñas no coinciden'
        
        return errors
    
    def process_invitation(self, code, new_user):
        """Procesa código de invitación y da recompensas"""
        try:
            from .models import Invitation
            invitation = Invitation.objects.get(code=code, accepted=False)
            
            # Marcar como aceptada
            invitation.accepted = True
            invitation.accepted_by = new_user
            invitation.accepted_at = datetime.now()
            invitation.save()
            
            # Dar 10 análisis extra al nuevo usuario
            new_user.profile.analyses_limit_monthly += 10
            new_user.profile.save()
            
            # Si el invitador tiene 3 invitaciones aceptadas, upgrade a Pro
            accepted_count = Invitation.objects.filter(
                inviter=invitation.inviter,
                accepted=True
            ).count()
            
            if accepted_count >= 3 and invitation.inviter.profile.plan == 'free':
                invitation.inviter.profile.upgrade_plan('pro')
                # Notificar al invitador (email o notificación)
                
        except Invitation.DoesNotExist:
            pass  # Código inválido, ignorar silenciosamente
    
    def get_client_ip(self, request):
        """Obtiene IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LoginView(View):
    """
    Login con email o username
    """
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/')
        
        next_url = request.GET.get('next', '/')
        return render(request, 'analyzer/auth/login.html', {'next': next_url})
    
    def post(self, request):
        try:
            data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
            
            username_or_email = data.get('username', '').strip()
            password = data.get('password', '')
            remember_me = data.get('remember_me', False)
            
            # Permitir login con email o username
            user = None
            if '@' in username_or_email:
                try:
                    user_obj = User.objects.get(email=username_or_email.lower())
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            else:
                user = authenticate(request, username=username_or_email, password=password)
            
            if user is not None:
                login(request, user)
                
                # Si no marca "recordarme", la sesión expira al cerrar navegador
                if not remember_me:
                    request.session.set_expiry(0)
                else:
                    request.session.set_expiry(1209600)  # 2 semanas
                
                # Log de uso
                UsageLog.objects.create(
                    user=user,
                    action='user_login',
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                # Verificar si necesita renovar plan
                if user.profile.plan != 'free' and user.profile.plan_expires:
                    if user.profile.plan_expires < datetime.now():
                        user.profile.upgrade_plan('free')  # Downgrade automático
                        messages.warning(request, 'Tu plan Pro ha expirado. Has vuelto al plan gratuito.')
                
                return JsonResponse({
                    'success': True,
                    'message': f'¡Bienvenido de vuelta, {user.username}!',
                    'redirect': request.POST.get('next', '/'),
                    'user': {
                        'username': user.username,
                        'plan': user.profile.get_plan_display(),
                        'analyses_remaining': user.profile.analyses_limit_monthly - user.profile.analyses_this_month
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Credenciales incorrectas'
                }, status=401)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Error al iniciar sesión'
            }, status=500)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LogoutView(View):
    """Logout seguro"""
    def post(self, request):
        if request.user.is_authenticated:
            UsageLog.objects.create(
                user=request.user,
                action='user_logout'
            )
            logout(request)
        
        return JsonResponse({'success': True, 'redirect': '/'})


class ProfileView(View):
    """
    Dashboard del usuario con estadísticas
    """
    @login_required
    def get(self, request):
        user = request.user
        profile = user.profile
        
        # Estadísticas del usuario
        from django.db.models import Count, Q
        from datetime import datetime, timedelta
        
        # Últimos 30 días
        last_30_days = datetime.now() - timedelta(days=30)
        
        analyses = AnalysisHistory.objects.filter(user=user)
        recent_analyses = analyses.filter(created_at__gte=last_30_days)
        
        # Estadísticas por plataforma
        platform_stats = analyses.values('platform').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Análisis por tipo
        type_stats = {
            'basic': analyses.filter(analysis_type='basic').count(),
            'competitive': analyses.filter(analysis_type='competitive').count()
        }
        
        context = {
            'profile': profile,
            'total_analyses': analyses.count(),
            'analyses_this_month': profile.analyses_this_month,
            'analyses_remaining': profile.analyses_limit_monthly - profile.analyses_this_month,
            'recent_analyses': recent_analyses.order_by('-created_at')[:5],
            'platform_stats': platform_stats,
            'type_stats': type_stats,
            'can_upgrade': profile.plan == 'free',
            'days_until_renewal': None
        }
        
        # Si tiene plan pago, calcular días hasta renovación
        if profile.plan != 'free' and profile.plan_expires:
            days_remaining = (profile.plan_expires - datetime.now()).days
            context['days_until_renewal'] = max(0, days_remaining)
        
        return render(request, 'analyzer/auth/profile.html', context)


class UpgradeView(View):
    """
    Vista para mostrar planes y upgrade (preparado para Stripe/PayPal futuro)
    """
    def get(self, request):
        plans = [
            {
                'name': 'Gratuito',
                'price': 0,
                'features': [
                    '5 análisis básicos por mes',
                    'Acceso a plantillas',
                    'Exportación PDF',
                    'Historial 30 días'
                ],
                'limitations': [
                    'Sin análisis competitivo',
                    'Sin API',
                    'Sin soporte prioritario'
                ],
                'current': request.user.is_authenticated and request.user.profile.plan == 'free'
            },
            {
                'name': 'Profesional',
                'price': 29,
                'features': [
                    '100 análisis por mes',
                    'Análisis competitivo ilimitado',
                    'Plantillas premium',
                    'Exportación PDF avanzada',
                    'Historial ilimitado',
                    'Dashboard analytics',
                    'Soporte por email'
                ],
                'limitations': [
                    'Sin acceso API'
                ],
                'current': request.user.is_authenticated and request.user.profile.plan == 'pro',
                'popular': True
            },
            {
                'name': 'Premium',
                'price': 99,
                'features': [
                    'Análisis ILIMITADOS',
                    'Todo lo de Pro',
                    'API REST completa',
                    'Análisis en lote',
                    'White label',
                    'Soporte prioritario 24/7',
                    'Entrenamiento personalizado'
                ],
                'limitations': [],
                'current': request.user.is_authenticated and request.user.profile.plan == 'premium'
            }
        ]
        
        return render(request, 'analyzer/auth/upgrade.html', {'plans': plans})
    
    def post(self, request):
        """
        Procesamiento de upgrade (por ahora simulado, preparado para pagos reales)
        """
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Debes iniciar sesión'}, status=401)
        
        plan = request.POST.get('plan')
        
        # Por ahora, solo permitir upgrade manual o con código promocional
        promo_code = request.POST.get('promo_code', '').strip()
        
        # Códigos de prueba (remover en producción)
        valid_codes = {
            'EARLY2024': 'pro',
            'PREMIUM2024': 'premium'
        }
        
        if promo_code in valid_codes:
            new_plan = valid_codes[promo_code]
            request.user.profile.upgrade_plan(new_plan)
            
            messages.success(request, f'¡Felicidades! Has sido actualizado al plan {new_plan.title()}')
            return JsonResponse({
                'success': True,
                'message': f'Actualizado a plan {new_plan.title()}',
                'redirect': '/profile/'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Código promocional inválido. Los pagos estarán disponibles pronto.'
            }, status=400)