# analyzer/views.py
# VERSIÓN ORIGINAL QUE FUNCIONABA - SIN SISTEMA DE USUARIOS

from django.shortcuts import render
from django.views import View
from django.http import JsonResponse, FileResponse
from .models import AnalysisHistory, MarketingTemplate
from .utils.scraping import scrape_product_info
from .utils.pdf_generator import generate_strategy_pdf
import json

# IMPORTA TU FUNCIÓN DE IA CORRECTA
try:
    from .utils.ai_integration import generate_strategy
except:
    # Si no existe, usa una temporal
    def generate_strategy(prompt, api_key):
        return "Estrategia temporal - revisa tu archivo ai_integration.py"

class AffiliateStrategistView(View):
    """Vista principal para el generador de estrategias"""
    
    def get(self, request):
        # Cargar plantillas si existen
        try:
            templates = MarketingTemplate.objects.filter(
                success_rate__gte=70
            ).order_by('-times_used')[:6]
        except:
            templates = []
        
        context = {
            'templates': templates
        }
        return render(request, 'analyzer/index.html', context)
    
    # REEMPLAZAR la función post() en AffiliateStrategistView en analyzer/views.py

def post(self, request):
    """Procesa el análisis del producto"""
    try:
        # ✅ VERIFICAR qué tipo de análisis se solicita
        analysis_type = request.POST.get('analysis_type', 'basic')
        
        # ✅ DEBUG: Imprimir qué se está enviando
        print(f"Analysis type recibido: {analysis_type}")
        print(f"POST data: {dict(request.POST)}")
        
        # ✅ CORREGIR la condición - debe ser 'competitive' no 'competitor'
        if analysis_type == 'competitive' or analysis_type == 'competitor':
            return self.competitive_analysis(request)
        else:
            return self.basic_analysis(request)
            
    except Exception as e:
        print(f"Error en post(): {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Error al procesar análisis: {str(e)}'
        })
    
    # REEMPLAZAR la función basic_analysis() en AffiliateStrategistView

def basic_analysis(self, request):
    """Análisis básico de producto - CORREGIDO"""
    try:
        # ✅ OBTENER datos del formulario con valores por defecto
        product_url = request.POST.get('product_url', '').strip()
        platform = request.POST.get('platform', 'tiktok')
        target_audience = request.POST.get('target_audience', '')
        additional_context = request.POST.get('additional_context', '')
        campaign_goal = request.POST.get('campaign_goal', 'conversions')
        budget = request.POST.get('budget', 'medium')
        tone = request.POST.get('tone', 'professional')
        api_key = request.POST.get('api_key', '')
        
        # ✅ VALIDAR que tenemos la URL del producto
        if not product_url:
            return JsonResponse({
                'success': False,
                'error': 'URL del producto es requerida'
            })
        
        # ✅ DEBUG: Ver qué datos tenemos
        print(f"Analizando producto: {product_url}")
        print(f"Plataforma: {platform}")
        print(f"Usuario: {request.user if request.user.is_authenticated else 'Anónimo'}")
        
        # ✅ SCRAPING del producto
        product_info = scrape_product_info(product_url)
        
        if not product_info['success']:
            return JsonResponse({
                'success': False,
                'error': 'No se pudo analizar el producto. Verifica la URL.'
            })
        
        # ✅ CONSTRUIR prompt para IA
        prompt = f"""
        Actúa como un experto en marketing de afiliados y genera una estrategia completa.
        
        PRODUCTO:
        - Título: {product_info['data'].get('title', 'Producto')}
        - Precio: {product_info['data'].get('price', 'No especificado')}
        - Descripción: {product_info['data'].get('description', 'No disponible')[:500]}
        
        CONFIGURACIÓN:
        - Plataforma: {platform}
        - Audiencia: {target_audience}
        - Objetivo: {campaign_goal}
        - Presupuesto: {budget}
        - Tono: {tone}
        - Contexto adicional: {additional_context}
        
        GENERA:
        
        ## 1. Análisis de Necesidades
        ¿Qué problema resuelve este producto para la audiencia?
        
        ## 2. Estrategia de Contenido
        - Tipo de contenido ideal
        - Formato recomendado
        - Frecuencia de publicación
        
        ## 3. Mensaje Principal
        - Hook principal
        - Puntos de dolor a atacar
        - Beneficios clave a destacar
        
        ## 4. Call to Action
        - CTA principal
        - CTAs secundarios
        - Urgencia/escasez
        
        ## 5. Hashtags y Keywords
        Proporciona hashtags específicos para {platform}
        
        ## 6. Métricas de Éxito
        - KPIs principales
        - Objetivos realistas
        
        Sé específico y actionable.
        """
        
        # ✅ GENERAR estrategia con IA
        ai_response = generate_strategy(prompt, api_key)
        
        # ✅ GUARDAR en historial
        analysis = AnalysisHistory.objects.create(
            user=request.user if request.user.is_authenticated else None,
            product_url=product_url,
            product_title=product_info['data'].get('title', 'Producto'),
            product_price=product_info['data'].get('price'),
            product_description=product_info['data'].get('description'),
            platform=platform,
            target_audience=target_audience,
            additional_context=additional_context,
            campaign_goal=campaign_goal,
            budget=budget,
            tone=tone,
            analysis_type='basic',
            ai_response=ai_response,
            success=True
        )
        
        # ✅ RESPUESTA EXITOSA
        return JsonResponse({
            'success': True,
            'analysis_id': analysis.id,
            'response': ai_response,
            'product': product_info['data']
        })
        
    except Exception as e:
        # ✅ MANEJO DE ERRORES detallado
        print(f"Error en basic_analysis: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Error al procesar análisis básico: {str(e)}'
        })
    
    # REEMPLAZAR la función competitive_analysis() en AffiliateStrategistView

def competitive_analysis(self, request):
    """Análisis competitivo de múltiples productos - CORREGIDO"""
    try:
        # ✅ OBTENER datos con valores por defecto y validación
        main_product_url = request.POST.get('main_product_url', '').strip()
        if not main_product_url:
            # Si no hay main_product_url, usar product_url como fallback
            main_product_url = request.POST.get('product_url', '').strip()
        
        platform = request.POST.get('platform', 'tiktok')
        target_audience = request.POST.get('target_audience', '')
        api_key = request.POST.get('api_key', '')
        
        # ✅ VALIDAR que tenemos la URL principal
        if not main_product_url:
            return JsonResponse({
                'success': False,
                'error': 'URL del producto principal es requerida para análisis competitivo'
            })
        
        # ✅ URLs de competidores (opcional para análisis competitivo)
        competitor_urls = []
        for i in range(1, 6):  # Hasta 5 competidores
            url = request.POST.get(f'competitor_{i}', '').strip()
            if url:
                competitor_urls.append(url)
        
        # ✅ DEBUG: Ver qué datos tenemos
        print(f"Análisis competitivo - Producto principal: {main_product_url}")
        print(f"Competidores encontrados: {len(competitor_urls)}")
        
        # ✅ SCRAPING del producto principal
        main_product = scrape_product_info(main_product_url)
        if not main_product['success']:
            return JsonResponse({
                'success': False,
                'error': 'No se pudo analizar el producto principal'
            })
        
        # ✅ SCRAPING de competidores (si existen)
        competitors_data = []
        if competitor_urls:
            for url in competitor_urls:
                comp_info = scrape_product_info(url)
                if comp_info['success']:
                    competitors_data.append(comp_info['data'])
        
        # ✅ ANÁLISIS de precios
        prices = []
        for comp in competitors_data:
            try:
                price_str = comp.get('price', '0')
                price = float(''.join(filter(str.isdigit, price_str.split('.')[0])))
                prices.append(price)
            except:
                pass
        
        main_price_str = main_product['data'].get('price', '0')
        try:
            main_price = float(''.join(filter(str.isdigit, main_price_str.split('.')[0])))
        except:
            main_price = 0
        
        # ✅ DETERMINAR posición de precio
        if prices:
            avg_price = sum(prices) / len(prices)
            if main_price > avg_price * 1.2:
                price_position = 'premium'
            elif main_price < avg_price * 0.8:
                price_position = 'economico'
            else:
                price_position = 'competitivo'
        else:
            price_position = 'sin_competencia'
        
        # ✅ CONSTRUIR prompt competitivo
        competitors_info = "\n".join([
            f"- {comp.get('title', 'Competidor')}: {comp.get('price', 'N/A')}"
            for comp in competitors_data
        ]) if competitors_data else "No se encontraron competidores para comparar"
        
        prompt = f"""
        Actúa como experto en competitive intelligence para marketing de afiliados.
        
        PRODUCTO PRINCIPAL:
        - Título: {main_product['data'].get('title')}
        - Precio: {main_product['data'].get('price')}
        - Posición de precio: {price_position}
        
        COMPETIDORES ANALIZADOS:
        {competitors_info}
        
        PLATAFORMA: {platform}
        AUDIENCIA: {target_audience}
        
        GENERA UN ANÁLISIS COMPETITIVO:
        
        ## POSICIONAMIENTO ESTRATÉGICO
        
        ### Tu Ventaja Competitiva Única
        ¿Cómo diferenciarte de la competencia?
        
        ### Gaps de Mercado Identificados
        ¿Qué NO están haciendo tus competidores?
        
        ## ESTRATEGIA DE PRECIO
        
        Tu precio es {price_position}. ¿Cómo comunicarlo?
        
        ## TÁCTICAS DE ATAQUE
        
        ### Para Robar Market Share
        5 tácticas específicas e inmediatas
        
        ### Ángulos No Explotados
        Oportunidades que la competencia ignora
        
        ## PLAN DE ACCIÓN INMEDIATO
        
        3 acciones para implementar HOY
        
        Sé MUY específico y agresivo en las recomendaciones.
        """
        
        # ✅ GENERAR estrategia competitiva
        ai_response = generate_strategy(prompt, api_key)
        
        # ✅ GUARDAR análisis
        analysis = AnalysisHistory.objects.create(
            user=request.user if request.user.is_authenticated else None,
            product_url=main_product_url,
            product_title=main_product['data'].get('title', 'Producto'),
            product_price=main_product['data'].get('price'),
            platform=platform,
            target_audience=target_audience,
            analysis_type='competitive',
            ai_response=ai_response,
            success=True,
            additional_data={
                'competitors_analyzed': len(competitors_data),
                'price_position': price_position,
                'competitors': competitors_data
            }
        )
        
        # ✅ RESPUESTA EXITOSA
        return JsonResponse({
            'success': True,
            'analysis_id': analysis.id,
            'response': ai_response,
            'main_product': main_product['data'],
            'competitors_analyzed': len(competitors_data),
            'pricing_analysis': {
                'position': price_position,
                'recommendation': f'Estrategia de precio: {price_position}'
            }
        })
        
    except Exception as e:
        # ✅ MANEJO DE ERRORES detallado
        print(f"Error en competitive_analysis: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Error en análisis competitivo: {str(e)}'
        })


# Vista para descargar PDF
def download_pdf(request, analysis_id):
    """Descarga el análisis como PDF"""
    try:
        analysis = AnalysisHistory.objects.get(id=analysis_id)
        pdf_buffer = generate_strategy_pdf(analysis)
        
        filename = f"estrategia_{analysis.product_title[:30]}_{analysis.id}.pdf"
        
        return FileResponse(
            pdf_buffer,
            as_attachment=True,
            filename=filename
        )
    except AnalysisHistory.DoesNotExist:
        return JsonResponse({'error': 'Análisis no encontrado'}, status=404)
    
    
# AGREGAR AL FINAL DE analyzer/views.py
# Vistas que faltan referenciadas en urls.py

class UserHistoryView(View):
    """Vista de historial para usuarios autenticados"""
    
    def get(self, request):
        # Si está autenticado, mostrar SUS análisis
        if request.user.is_authenticated:
            analyses = AnalysisHistory.objects.filter(
                user=request.user if hasattr(AnalysisHistory, 'user') else None
            ).order_by('-created_at')[:50] if hasattr(AnalysisHistory, 'user') else AnalysisHistory.objects.all()[:50]
        else:
            # Si no está autenticado, mostrar análisis públicos
            analyses = AnalysisHistory.objects.all().order_by('-created_at')[:20]
        
        context = {
            'analyses': analyses,
            'is_authenticated': request.user.is_authenticated,
            'user': request.user if request.user.is_authenticated else None,
            'total_analyses': analyses.count() if analyses else 0
        }
        
        return render(request, 'analyzer/history.html', context)


class PublicHistoryView(View):
    """Vista de historial público/compartido"""
    
    def get(self, request):
        # Mostrar solo análisis exitosos
        analyses = AnalysisHistory.objects.filter(
            success=True
        ).order_by('-created_at')[:30]
        
        context = {
            'analyses': analyses,
            'is_public': True,
            'total_analyses': analyses.count()
        }
        
        return render(request, 'analyzer/public_history.html', context)