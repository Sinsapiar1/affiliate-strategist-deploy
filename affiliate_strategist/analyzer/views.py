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
    
    def post(self, request):
        """Procesa el análisis del producto"""
        analysis_type = request.POST.get('analysis_type', 'basic')
        
        if analysis_type == 'competitor':
            return self.competitive_analysis(request)
        else:
            return self.basic_analysis(request)
    
    def basic_analysis(self, request):
        """Análisis básico de producto"""
        try:
            # Obtener datos del formulario
            product_url = request.POST.get('product_url')
            platform = request.POST.get('platform')
            target_audience = request.POST.get('target_audience')
            additional_context = request.POST.get('additional_context', '')
            campaign_goal = request.POST.get('campaign_goal', 'conversions')
            budget = request.POST.get('budget', 'medium')
            tone = request.POST.get('tone', 'professional')
            api_key = request.POST.get('api_key')
            
            # Scraping del producto
            product_info = scrape_product_info(product_url)
            
            if not product_info['success']:
                return JsonResponse({
                    'success': False,
                    'error': 'No se pudo analizar el producto. Verifica la URL.'
                })
            
            # Construir prompt para IA
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
            
            # Generar estrategia con IA
            ai_response = generate_strategy(prompt, api_key)
            
            # Guardar en historial
            analysis = AnalysisHistory.objects.create(
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
            
            return JsonResponse({
                'success': True,
                'analysis_id': analysis.id,
                'response': ai_response,
                'product': product_info['data']
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al procesar: {str(e)}'
            })
    
    def competitive_analysis(self, request):
        """Análisis competitivo de múltiples productos"""
        try:
            # Producto principal
            main_product_url = request.POST.get('main_product_url')
            platform = request.POST.get('platform')
            target_audience = request.POST.get('target_audience')
            api_key = request.POST.get('api_key')
            
            # URLs de competidores
            competitor_urls = []
            for i in range(1, 6):  # Hasta 5 competidores
                url = request.POST.get(f'competitor_{i}')
                if url:
                    competitor_urls.append(url)
            
            if not competitor_urls:
                return JsonResponse({
                    'success': False,
                    'error': 'Debes agregar al menos un competidor'
                })
            
            # Scraping del producto principal
            main_product = scrape_product_info(main_product_url)
            if not main_product['success']:
                return JsonResponse({
                    'success': False,
                    'error': 'No se pudo analizar el producto principal'
                })
            
            # Scraping de competidores
            competitors_data = []
            for url in competitor_urls:
                comp_info = scrape_product_info(url)
                if comp_info['success']:
                    competitors_data.append(comp_info['data'])
            
            # Análisis de precios
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
            
            # Determinar posición de precio
            if prices:
                avg_price = sum(prices) / len(prices)
                if main_price > avg_price * 1.2:
                    price_position = 'premium'
                elif main_price < avg_price * 0.8:
                    price_position = 'economico'
                else:
                    price_position = 'competitivo'
            else:
                price_position = 'unknown'
            
            # Construir prompt competitivo
            competitors_info = "\n".join([
                f"- {comp.get('title', 'Competidor')}: {comp.get('price', 'N/A')}"
                for comp in competitors_data
            ])
            
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
            
            # Generar estrategia competitiva
            ai_response = generate_strategy(prompt, api_key)
            
            # Guardar análisis
            analysis = AnalysisHistory.objects.create(
                product_url=main_product_url,
                product_title=main_product['data'].get('title', 'Producto'),
                product_price=main_product['data'].get('price'),
                platform=platform,
                target_audience=target_audience,
                analysis_type='competitive',
                ai_response=ai_response,
                success=True,
                # Guardar datos de competencia en JSON
                additional_data={
                    'competitors_analyzed': len(competitors_data),
                    'price_position': price_position,
                    'competitors': competitors_data
                }
            )
            
            return JsonResponse({
                'success': True,
                'analysis_id': analysis.id,
                'response': ai_response,
                'main_product': main_product['data'],
                'competitors_analyzed': len(competitors_data),
                'pricing_analysis': {
                    'position': price_position,
                    'recommendation': 'Ajusta tu estrategia según tu posición de precio'
                }
            })
            
        except Exception as e:
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
# Estas son las vistas que faltan en tu urls.py
# AGREGAR AL FINAL DE analyzer/views.py
# Vistas de historial faltantes (compatibles con tu sistema de auth)

class UserHistoryView(View):
    """Vista de historial para usuarios autenticados"""
    
    def get(self, request):
        # Si el usuario está autenticado, mostrar SUS análisis
        if request.user.is_authenticated:
            analyses = AnalysisHistory.objects.filter(
                user=request.user
            ).order_by('-created_at')[:50]
            
            context = {
                'analyses': analyses,
                'is_authenticated': True,
                'user': request.user,
                'total_analyses': analyses.count()
            }
        else:
            # Si no está autenticado, mostrar análisis públicos/anónimos
            analyses = AnalysisHistory.objects.filter(
                user__isnull=True  # Análisis sin usuario asignado
            ).order_by('-created_at')[:20]
            
            context = {
                'analyses': analyses,
                'is_authenticated': False,
                'total_analyses': analyses.count()
            }
        
        return render(request, 'analyzer/history.html', context)


class PublicHistoryView(View):
    """Vista de historial público/compartido"""
    
    def get(self, request):
        # Mostrar solo análisis exitosos y públicos
        analyses = AnalysisHistory.objects.filter(
            success=True
        ).order_by('-created_at')[:20]
        
        context = {
            'analyses': analyses,
            'is_public': True,
            'total_analyses': analyses.count()
        }
        
        return render(request, 'analyzer/public_history.html', context)