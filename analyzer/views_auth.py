# analyzer/views_auth.py - SOLUCIÓN DEFINITIVA
# ✅ REEMPLAZAR COMPLETAMENTE TU ARCHIVO views_auth.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.views import View
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
import re

class RegisterView(View):
    """
    Registro simplificado pero robusto
    """
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'analyzer/auth/register.html')
    
    def post(self, request):
        try:
            # ✅ Manejar tanto JSON como formulario
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
            
            username = data.get('username', '').strip()
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            password2 = data.get('password2', '')
            company = data.get('company_name', '').strip()
            
            # ✅ Validaciones
            errors = self.validate_registration(username, email, password, password2)
            if errors:
                for field, error in errors.items():
                    messages.error(request, error)
                return render(request, 'analyzer/auth/register.html')
            
            # ✅ Crear usuario
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                # Asegurar perfil
                try:
                    from .models import UserProfile
                    UserProfile.objects.get_or_create(user=user)
                except Exception:
                    pass
                
                # ✅ Guardar información adicional en el perfil del usuario
                if company:
                    user.first_name = company  # Usar first_name para empresa temporalmente
                    user.save()
                
                # ✅ Auto-login
                login(request, user)
                
                # ✅ Mensaje de éxito
                messages.success(request, f'¡Bienvenido {username}! Tu cuenta ha sido creada exitosamente.')
                
                # ✅ Responder según el tipo de petición
                if request.content_type == 'application/json':
                    return JsonResponse({
                        'success': True,
                        'message': f'¡Bienvenido {username}!',
                        'redirect': '/',
                        'user': {
                            'username': user.username,
                            'email': user.email
                        }
                    })
                else:
                    return redirect('/')
                
        except Exception as e:
            error_msg = 'Error al crear la cuenta. Intenta nuevamente.'
            messages.error(request, error_msg)
            
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': False,
                    'error': error_msg
                }, status=500)
            else:
                return render(request, 'analyzer/auth/register.html')
    
    def validate_registration(self, username, email, password, password2):
        """Validación completa pero simplificada"""
        errors = {}
        
        # Username
        if not username or len(username) < 3:
            errors['username'] = 'El nombre de usuario debe tener al menos 3 caracteres'
        elif not re.match(r'^[\w.@+-]+$', username):
            errors['username'] = 'Nombre de usuario inválido'
        elif User.objects.filter(username=username).exists():
            errors['username'] = 'Este nombre de usuario ya existe'
        
        # Email
        try:
            validate_email(email)
            if User.objects.filter(email=email).exists():
                errors['email'] = 'Este email ya está registrado'
        except ValidationError:
            errors['email'] = 'Email inválido'
        
        # Password
        if len(password) < 6:
            errors['password'] = 'La contraseña debe tener al menos 6 caracteres'
        elif password != password2:
            errors['password2'] = 'Las contraseñas no coinciden'
        
        return errors


class LoginView(View):
    """
    Login robusto con email o username
    """
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/')
        
        next_url = request.GET.get('next', '/')
        return render(request, 'analyzer/auth/login.html', {'next': next_url})
    
    def post(self, request):
        try:
            # ✅ Manejar tanto JSON como formulario
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
            
            username_or_email = data.get('username', '').strip()
            password = data.get('password', '')
            remember_me = data.get('remember_me', False)
            
            # ✅ Autenticación flexible
            user = None
            
            # Intentar con email
            if '@' in username_or_email:
                try:
                    user_obj = User.objects.get(email=username_or_email.lower())
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            # Si no funcionó con email, intentar con username
            if user is None:
                user = authenticate(request, username=username_or_email, password=password)
            
            # ✅ Login exitoso
            if user is not None and user.is_active:
                login(request, user)
                
                # ✅ Configurar duración de sesión
                if not remember_me:
                    request.session.set_expiry(0)  # Expira al cerrar navegador
                else:
                    request.session.set_expiry(1209600)  # 2 semanas
                
                success_msg = f'¡Bienvenido de vuelta, {user.username}!'
                messages.success(request, success_msg)
                
                # ✅ Responder según tipo de petición
                if request.content_type == 'application/json':
                    return JsonResponse({
                        'success': True,
                        'message': success_msg,
                        'redirect': data.get('next', '/'),
                        'user': {
                            'username': user.username,
                            'email': user.email
                        }
                    })
                else:
                    next_url = data.get('next', '/')
                    return redirect(next_url)
            else:
                # ✅ Login fallido
                error_msg = 'Usuario o contraseña incorrectos'
                messages.error(request, error_msg)
                
                if request.content_type == 'application/json':
                    return JsonResponse({
                        'success': False,
                        'error': error_msg
                    }, status=401)
                else:
                    return render(request, 'analyzer/auth/login.html')
                
        except Exception as e:
            error_msg = 'Error al iniciar sesión'
            messages.error(request, error_msg)
            
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': False,
                    'error': error_msg
                }, status=500)
            else:
                return render(request, 'analyzer/auth/login.html')


class LogoutView(View):
    """Logout seguro"""
    def get(self, request):
        return self.post(request)
    
    def post(self, request):
        if request.user.is_authenticated:
            username = request.user.username
            logout(request)
            messages.info(request, f'Hasta luego, {username}!')
        
        if request.content_type == 'application/json':
            return JsonResponse({'success': True, 'redirect': '/'})
        else:
            return redirect('/')


class ProfileView(View):
    """
    Perfil de usuario simplificado
    """
    def get(self, request):
        if not request.user.is_authenticated:
            messages.warning(request, 'Debes iniciar sesión para ver tu perfil')
            return redirect('/login/')
        
        # ✅ Estadísticas del usuario
        from .models import AnalysisHistory
        try:
            user_analyses = AnalysisHistory.objects.filter(
                user=request.user if hasattr(AnalysisHistory, 'user') else None
            ).order_by('-created_at')[:5]
            total_analyses = user_analyses.count() if user_analyses else 0
        except:
            user_analyses = []
            total_analyses = 0
        
        context = {
            'user': request.user,
            'total_analyses': total_analyses,
            'recent_analyses': user_analyses,
            'company': request.user.first_name if request.user.first_name else None,
        }
        
        return render(request, 'analyzer/auth/profile.html', context)


# analyzer/views_auth.py - REEMPLAZAR la clase UpgradeView

class UpgradeView(View):
    """Vista de planes con funcionalidad real"""
    
    def get(self, request):
        user_plan = 'free'
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            user_plan = request.user.profile.plan
        
        plans = [
            {
                'id': 'free',
                'name': 'Gratuito',
                'price': 0,
                'price_display': 'Gratis',
                'features': [
                    '✅ 5 análisis básicos por mes',
                    '✅ Descarga en PDF',
                    '✅ Historial de análisis',
                    '❌ Sin análisis competitivos',
                    '❌ Sin plantillas premium',
                    '❌ Sin soporte prioritario'
                ],
                'current': user_plan == 'free',
                'button_text': 'Plan Actual' if user_plan == 'free' else 'Cambiar a Gratis',
                'button_class': 'btn-secondary' if user_plan == 'free' else 'btn-outline-secondary'
            },
            {
                'id': 'pro',
                'name': 'Profesional',
                'price': 19,
                'price_display': '$19/mes',
                'features': [
                    '✅ 100 análisis por mes',
                    '✅ Análisis competitivos ilimitados',
                    '✅ Todas las plantillas premium',
                    '✅ Exportación en Excel',
                    '✅ Soporte prioritario',
                    '✅ Sin marca de agua en PDFs'
                ],
                'current': user_plan == 'pro',
                'recommended': True,
                'button_text': 'Plan Actual' if user_plan == 'pro' else 'Actualizar a Pro',
                'button_class': 'btn-primary' if user_plan != 'pro' else 'btn-secondary'
            },
            {
                'id': 'premium',
                'name': 'Premium',
                'price': 49,
                'price_display': '$49/mes',
                'features': [
                    '✅ Análisis ILIMITADOS',
                    '✅ Todas las funciones Pro',
                    '✅ API Access',
                    '✅ Análisis en lote',
                    '✅ White label',
                    '✅ Soporte 24/7',
                    '✅ Entrenamiento personalizado'
                ],
                'current': user_plan == 'premium',
                'button_text': 'Plan Actual' if user_plan == 'premium' else 'Actualizar a Premium',
                'button_class': 'btn-warning' if user_plan != 'premium' else 'btn-secondary'
            }
        ]
        
        context = {
            'plans': plans,
            'current_plan': user_plan,
            'is_authenticated': request.user.is_authenticated
        }
        
        if request.user.is_authenticated:
            profile = request.user.profile
            context.update({
                'analyses_used': profile.analyses_this_month,
                'analyses_limit': profile.analyses_limit_monthly,
                'analyses_remaining': profile.analyses_remaining
            })
        
        return render(request, 'analyzer/auth/upgrade.html', context)
    
    def post(self, request):
        """Procesar cambio de plan (aquí integrarías Stripe/PayPal)"""
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Debes iniciar sesión'}, status=401)
        
        new_plan = request.POST.get('plan')
        
        # Por ahora, cambio directo (aquí iría el proceso de pago)
        if new_plan in ['pro', 'premium']:
            # Aquí integrarías Stripe/PayPal
            # Por ahora, simulamos upgrade gratuito para testing
            request.user.profile.upgrade_plan(new_plan, 30)
            
            return JsonResponse({
                'success': True,
                'message': f'¡Actualizado a plan {new_plan.title()}!',
                'redirect': '/profile/'
            })
        
        return JsonResponse({'error': 'Plan no válido'}, status=400)