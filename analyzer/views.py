from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import AnalysisHistory
from .utils.ai_integration import detect_and_generate
from .utils.pdf_generator import generate_strategy_pdf
from uuid import UUID
import json

@require_http_methods(["GET", "POST"])
def home(request):
    """Página de inicio y endpoint para crear análisis vía POST"""
    if request.method == 'GET':
        # Asegura perfil si está autenticado
        if request.user.is_authenticated and not hasattr(request.user, 'profile'):
            try:
                from .models import UserProfile
                UserProfile.objects.get_or_create(user=request.user)
            except Exception:
                pass
        return render(request, 'analyzer/index.html')

    # POST: procesar análisis
    analysis_type = request.POST.get('analysis_type', 'basic')
    product_url = request.POST.get('product_url') or request.POST.get('main_product_url')
    platform = (request.POST.get('platform') or 'tiktok').lower()
    target_audience = request.POST.get('target_audience', '')
    campaign_goal = request.POST.get('campaign_goal', 'conversions')
    tone = request.POST.get('tone', 'professional')
    api_key = request.POST.get('api_key', '').strip()

    if not product_url or not api_key:
        return JsonResponse({'success': False, 'error': 'Faltan datos: URL del producto y API key son obligatorias.'}, status=400)

    # Lógica de límites: anónimo -> limitado por IP (middleware); autenticado -> por plan mensual
    if request.user.is_authenticated:
        # Garantiza que exista perfil
        if not hasattr(request.user, 'profile'):
            try:
                from .models import UserProfile
                UserProfile.objects.get_or_create(user=request.user)
            except Exception:
                pass
        # Asegurar reset mensual antes de evaluar límite
        if hasattr(request.user, 'profile'):
            try:
                request.user.profile.reset_monthly_counter_if_needed()
            except Exception:
                pass
        if hasattr(request.user, 'profile') and not request.user.profile.can_analyze():
            return JsonResponse({
                'success': False,
                'limit_reached': True,
                'error': 'Has alcanzado tu límite mensual. Actualiza tu plan para continuar.',
                'upgrade_url': '/upgrade/'
            }, status=429)

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
        return JsonResponse({'success': False, 'error': ai_result.get('error', 'Error generando estrategia')}, status=400)

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

        # Actualizar contadores si aplica
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            try:
                request.user.profile.add_analysis_count()
            except Exception:
                pass

        return JsonResponse({
            'success': True,
            'analysis_id': str(analysis.id),
            'response': analysis.ai_response,
            'product': {
                'title': analysis.product_title,
                'price': analysis.product_price,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'No se pudo guardar el análisis: {str(e)}'}, status=500)


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
