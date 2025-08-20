# analyzer/monetization.py - PRIMERA HERRAMIENTA DE MONETIZACIÓN

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import UserProfile, AnalysisHistory
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class MonetizationEngine:
    """
    Motor de monetización inteligente
    """
    
    @staticmethod
    def get_user_monetization_status(user):
        """Obtiene estado de monetización del usuario"""
        if not user.is_authenticated:
            return {
                'type': 'anonymous',
                'plan': 'none',
                'analyses_used': 0,
                'analyses_limit': 2,
                'analyses_remaining': 2,
                'should_show_upgrade': True,
                'urgency_level': 'high',
                'message': '🚫 Solo 2 análisis gratuitos por día. ¡Regístrate para 5 análisis mensuales!'
            }
        
        profile = user.profile
        
        # Calcular urgencia basada en uso
        usage_percentage = (profile.analyses_this_month / profile.analyses_limit_monthly) * 100
        
        if usage_percentage >= 100:
            urgency = 'critical'
            message = '🚨 ¡Límite alcanzado! Upgrade para continuar generando estrategias.'
        elif usage_percentage >= 80:
            urgency = 'high'
            message = f'⚠️ Solo {profile.analyses_remaining} análisis restantes este mes.'
        elif usage_percentage >= 60:
            urgency = 'medium'
            message = f'📊 {profile.analyses_remaining} análisis disponibles. ¿Considerando upgrade?'
        else:
            urgency = 'low'
            message = f'✅ {profile.analyses_remaining} análisis disponibles.'
        
        return {
            'type': 'registered',
            'plan': profile.plan,
            'analyses_used': profile.analyses_this_month,
            'analyses_limit': profile.analyses_limit_monthly,
            'analyses_remaining': profile.analyses_remaining,
            'should_show_upgrade': profile.plan == 'free' and usage_percentage >= 60,
            'urgency_level': urgency,
            'message': message,
            'usage_percentage': round(usage_percentage, 1)
        }
    
    @staticmethod
    def get_upgrade_incentives(user_status):
        """Genera incentivos personalizados para upgrade"""
        incentives = []
        
        if user_status['type'] == 'anonymous':
            incentives = [
                "🎯 5 análisis mensuales vs 2 diarios",
                "📊 Historial permanente de tus estrategias", 
                "📄 Descarga ilimitada de PDFs",
                "🚀 Análisis competitivos avanzados",
                "⚡ Sin esperas entre análisis"
            ]
        
        elif user_status['urgency_level'] == 'critical':
            incentives = [
                "🔥 ANÁLISIS ILIMITADOS con Pro",
                "📈 Análisis competitivos avanzados",
                "🎨 Plantillas premium exclusivas",
                "📊 Métricas y analytics detallados",
                "🏆 Soporte prioritario 24/7"
            ]
        
        elif user_status['urgency_level'] == 'high':
            incentives = [
                "📈 100 análisis/mes con plan Pro",
                "🎯 Análisis competitivos incluidos",
                "📊 Templates premium",
                "🚀 Procesamiento más rápido"
            ]
        
        else:
            incentives = [
                "🚀 Upgrade cuando llegues al límite",
                "📈 Análisis competitivos disponibles",
                "🎨 Plantillas premium esperándote"
            ]
        
        return incentives
    
    @staticmethod
    def should_block_analysis(user):
        """Determina si debe bloquear análisis para monetización"""
        if not user.is_authenticated:
            # Verificar límite anónimo (se hace en middleware)
            return False
        
        profile = user.profile
        
        # Bloquear si excede límite mensual (excepto premium)
        if profile.plan != 'premium' and profile.analyses_this_month >= profile.analyses_limit_monthly:
            return True
        
        return False

# Views de monetización
@login_required
def upgrade_page(request):
    """Página de upgrade personalizada"""
    user_status = MonetizationEngine.get_user_monetization_status(request.user)
    incentives = MonetizationEngine.get_upgrade_incentives(user_status)
    
    # Planes con precios reales
    plans = [
        {
            'id': 'free',
            'name': 'Gratuito',
            'price': 0,
            'price_display': 'Gratis',
            'analyses_limit': 5,
            'features': [
                '✅ 5 análisis básicos por mes',
                '✅ Descarga en PDF', 
                '✅ Historial personal',
                '❌ Sin análisis competitivos',
                '❌ Sin plantillas premium'
            ],
            'current': user_status['plan'] == 'free',
            'popular': False
        },
        {
            'id': 'pro',
            'name': 'Profesional',
            'price': 19,
            'price_display': '$19/mes',
            'analyses_limit': 100,
            'features': [
                '🚀 100 análisis por mes',
                '🎯 Análisis competitivos incluidos',
                '📈 Plantillas premium',
                '📊 Exportación avanzada',
                '⚡ Procesamiento prioritario'
            ],
            'current': user_status['plan'] == 'pro',
            'popular': True
        },
        {
            'id': 'premium',
            'name': 'Premium',
            'price': 49,
            'price_display': '$49/mes',
            'analyses_limit': 999999,
            'features': [
                '🔥 Análisis ILIMITADOS',
                '🏆 Todas las funciones Pro',
                '🎨 Templates exclusivos',
                '📞 Soporte 24/7',
                '🚀 API Access'
            ],
            'current': user_status['plan'] == 'premium',
            'popular': False
        }
    ]
    
    context = {
        'user_status': user_status,
        'incentives': incentives,
        'plans': plans,
        'urgency_message': user_status['message']
    }
    
    return render(request, 'analyzer/monetization/upgrade.html', context)

@require_http_methods(["POST"])
@login_required  
def process_upgrade(request):
    """Procesa upgrade de plan (integrar con Stripe aquí)"""
    new_plan = request.POST.get('plan')
    
    if new_plan not in ['pro', 'premium']:
        return JsonResponse({'error': 'Plan inválido'}, status=400)
    
    try:
        # Aquí integrarías Stripe/PayPal
        # Por ahora, upgrade directo para testing
        profile = request.user.profile
        
        if new_plan == 'pro':
            profile.upgrade_plan('pro', 30)
            message = '🎉 ¡Upgrade a Pro exitoso! Ahora tienes 100 análisis mensuales.'
        else:
            profile.upgrade_plan('premium', 30) 
            message = '🔥 ¡Upgrade a Premium exitoso! Análisis ilimitados desbloqueados.'
        
        logger.info(f"💰 UPGRADE: {request.user.username} -> {new_plan}")
        
        return JsonResponse({
            'success': True,
            'message': message,
            'new_plan': new_plan,
            'redirect': '/'
        })
        
    except Exception as e:
        logger.error(f"Error processing upgrade: {e}")
        return JsonResponse({
            'error': 'Error procesando upgrade. Intenta de nuevo.'
        }, status=500)

def monetization_popup_data(request):
    """API para obtener datos del popup de monetización"""
    if request.user.is_authenticated:
        user_status = MonetizationEngine.get_user_monetization_status(request.user)
        incentives = MonetizationEngine.get_upgrade_incentives(user_status)
    else:
        user_status = MonetizationEngine.get_user_monetization_status(None)
        incentives = MonetizationEngine.get_upgrade_incentives(user_status)
    
    return JsonResponse({
        'user_status': user_status,
        'incentives': incentives,
        'show_popup': user_status['should_show_upgrade']
    })