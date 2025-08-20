from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import AnalysisHistory
from django.core.cache import cache
from .utils.ai_integration import detect_and_generate
from .utils.pdf_generator import generate_strategy_pdf
from uuid import UUID
import json
import logging

@require_http_methods(["GET", "POST"])
def home(request):
    """Página de inicio y endpoint para crear análisis vía POST"""
    logger = logging.getLogger(__name__)
    
    if request.method == 'GET':
        # Crear perfil si está autenticado y no lo tiene
        if request.user.is_authenticated:
            try:
                from .models import UserProfile
                profile, created = UserProfile.objects.get_or_create(
                    user=request.user,
                    defaults={
                        'plan': 'free',
                        'analyses_limit_monthly': 5,
                        'analyses_this_month': 0
                    }
                )
                if created:
                    logger.info(f"✅ Perfil creado para {request.user.username}")
            except Exception as e:
                logger.error(f"❌ Error creando perfil: {str(e)}")
        
        return render(request, 'analyzer/index.html')

    # POST: procesar análisis
    analysis_type = request.POST.get('analysis_type', 'basic')
    product_url = request.POST.get('product_url') or request.POST.get('main_product_url')
    platform = (request.POST.get('platform') or 'tiktok').lower()
    target_audience = request.POST.get('target_audience', '')
    campaign_goal = request.POST.get('campaign_goal', 'conversions')
    tone = request.POST.get('tone', 'professional')
    api_key = request.POST.get('api_key', '').strip()

    logger.info(f"🔄 Análisis solicitado: {analysis_type} - {product_url} - Usuario: {request.user.username if request.user.is_authenticated else 'Anónimo'}")

    if not product_url or not api_key:
        return JsonResponse({
            'success': False, 
            'error': 'Faltan datos: URL del producto y API key son obligatorias.'
        }, status=400)

    # Lógica de límites: anónimo -> limitado por IP (middleware); autenticado -> por plan mensual
    if request.user.is_authenticated:
        try:
            # Crear perfil si no existe
            from .models import UserProfile
            profile, created = UserProfile.objects.get_or_create(
                user=request.user,
                defaults={
                    'plan': 'free',
                    'analyses_limit_monthly': 5,
                    'analyses_this_month': 0
                }
            )
            
            # Solo verificar, NO incrementar aún
            if not profile.can_analyze_atomic():
                logger.warning(f"🚫 Límite mensual alcanzado para {request.user.username}")
                return JsonResponse({
                    'success': False,
                    'limit_reached': True,
                    'error': f'Has alcanzado tu límite mensual ({profile.analyses_limit_monthly}). ¡Upgrade para continuar!',
                    'upgrade_url': '/upgrade/',
                    'current_count': profile.analyses_this_month,
                    'limit': profile.analyses_limit_monthly,
                    'plan': profile.plan
                }, status=429)
                
        except Exception as e:
            logger.error(f"❌ Error verificando límites: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Error interno verificando límites'
            }, status=500)

    # Idempotencia breve para evitar doble envío accidental (20s)
    try:
        import hashlib
        def _get_client_ip(req):
            xff = req.META.get('HTTP_X_FORWARDED_FOR')
            return xff.split(',')[0].strip() if xff else req.META.get('REMOTE_ADDR', '127.0.0.1')
        identity = f"user:{request.user.id}" if request.user.is_authenticated else f"ip:{_get_client_ip(request)}"
        base_string = f"{product_url}|{platform}|{target_audience}|{campaign_goal}|{tone}"
        token = hashlib.md5(base_string.encode()).hexdigest()
        dedupe_key = f"analyze_dedupe:{identity}:{token}"
        if cache.get(dedupe_key):
            return JsonResponse({
                'success': False,
                'error': 'Petición duplicada detectada. Espera unos segundos e intenta de nuevo.'
            }, status=409)
        # Pre-marcar para evitar duplicación en ráfaga
        cache.set(dedupe_key, True, 20)
    except Exception:
        # Si falla, continuar sin idempotencia
        pass

    # Construir prompt simple (puedes mejorar con más contexto)
    prompt_parts = [
        f"Genera una estrategia de marketing para el producto en {product_url}.",
        f"Plataforma: {platform}.",
        f"Audiencia objetivo: {target_audience or 'general'}.",
        f"Objetivo: {campaign_goal}.",
        f"Tono: {tone}.",
    ]
    if analysis_type == 'competitive':
        prompt_parts.insert(0, 'Análisis competitivo: compara con competidores similares y destaca ventajas.')
    prompt = '\n'.join(prompt_parts)

    ai_result = detect_and_generate(prompt, api_key)
    if not ai_result.get('success'):
        logger.error(f"❌ Error IA: {ai_result.get('error')}")
        return JsonResponse({
            'success': False, 
            'error': ai_result.get('error', 'Error generando estrategia')
        }, status=400)

    # Guardar análisis
    try:
        analysis = AnalysisHistory.objects.create(
            user=request.user if request.user.is_authenticated else None,
            product_url=product_url,
            product_title='Producto analizado',
            product_description=None,
            platform=platform,
            target_audience=target_audience,
            campaign_goal=campaign_goal,
            budget='medium',
            tone=tone,
            analysis_type=analysis_type,
            ai_response=ai_result['response'],
            success=True
        )

        # Incrementar contadores SOLO después de análisis exitoso
        if request.user.is_authenticated and analysis.success:
            try:
                # Incrementar SOLO una vez por análisis exitoso
                incremented = request.user.profile.add_analysis_count_atomic()
                if not incremented:
                    logger.warning(f"⚠️ Análisis creado pero contador no incrementado para {request.user.username}")
            except Exception as e:
                logger.error(f"❌ Error incrementando contador: {str(e)}")

        return JsonResponse({
            'success': True,
            'analysis_id': str(analysis.id),
            'response': analysis.ai_response,
            'product': {
                'title': analysis.product_title,
                'price': analysis.product_price,
            },
            # Estado de contador para refrescar UI en cliente
            **({
                'usage': {
                    'this_month': request.user.profile.analyses_this_month,
                    'limit': request.user.profile.analyses_limit_monthly,
                    'remaining': request.user.profile.analyses_remaining,
                    'plan': request.user.profile.plan
                }
            } if request.user.is_authenticated and hasattr(request.user, 'profile') else {})
        })
    except Exception as e:
        logger.error(f"❌ Error guardando análisis: {str(e)}")
        # Limpiar marca de idempotencia si falló creación
        try:
            cache.delete(dedupe_key)
        except Exception:
            pass
        return JsonResponse({
            'success': False, 
            'error': f'No se pudo guardar el análisis: {str(e)}'
        }, status=500)


def history(request):
    """Historial del usuario autenticado o mensaje si es anónimo"""
    analyses = []
    total_analyses = 0
    if request.user.is_authenticated:
        analyses = AnalysisHistory.objects.filter(user=request.user).order_by('-created_at')[:50]
        total_analyses = analyses.count()
    context = {
        'analyses': analyses,
        'total_analyses': total_analyses,
        'is_authenticated': request.user.is_authenticated,
    }
    return render(request, 'analyzer/history.html', context)


def public_history(request):
    """Historial público de análisis exitosos"""
    analyses = AnalysisHistory.objects.filter(success=True, is_public=True).order_by('-created_at')[:50]
    context = {
        'analyses': analyses,
        'total_analyses': analyses.count(),
    }
    return render(request, 'analyzer/public_history.html', context)


def download_pdf(request, analysis_id):
    """Descarga PDF para un análisis"""
    # analysis_id ya viene validado por el converter <uuid:>
    analysis = get_object_or_404(AnalysisHistory, id=analysis_id)
    pdf_bytes = generate_strategy_pdf(analysis)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="analysis_{analysis.id}.pdf"'
    return response
