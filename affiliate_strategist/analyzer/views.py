# analyzer/views.py - VERSIÓN MEJORADA Y ROBUSTA

from django.shortcuts import render
from django.views import View
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
import re
from datetime import datetime, timedelta
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
import json
import logging

from .models import AnalysisHistory, MarketingTemplate
from .utils.scraping import scrape_product_info
from .utils.pdf_generator import generate_strategy_pdf

# ✅ CONFIGURAR LOGGING
logger = logging.getLogger(__name__)

# ✅ IMPORTAR FUNCIÓN DE IA CON FALLBACK
try:
    from .utils.ai_integration import generate_strategy
except ImportError:
    logger.warning("AI integration not found, using fallback")
    def generate_strategy(prompt, api_key):
        return "⚠️ Función de IA no disponible. Configura tu integración con Gemini."

class AffiliateStrategistView(View):
    """Vista principal mejorada con mejor manejo de errores"""
    
    def dispatch(self, request, *args, **kwargs):
        """Debug y logging de requests"""
        logger.info(f"[DEBUG] {request.method} request to {request.path} from {request.META.get('REMOTE_ADDR')}")
        if request.method == 'POST':
            logger.info(f"[DEBUG] POST data keys: {list(request.POST.keys())}")
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        """Página principal con datos contextuales"""
        try:
            # ✅ ESTADÍSTICAS PARA EL USUARIO
            context = {
                'user': request.user,
                'is_authenticated': request.user.is_authenticated,
            }
            
            # ✅ Si está autenticado, agregar estadísticas personales
            if request.user.is_authenticated:
                user_analyses = AnalysisHistory.objects.filter(user=request.user)
                context.update({
                    'user_total_analyses': user_analyses.count(),
                    'user_successful_analyses': user_analyses.filter(success=True).count(),
                    'user_recent_analyses': user_analyses.order_by('-created_at')[:3],
                })
            
            # ✅ ESTADÍSTICAS GENERALES
            total_analyses = AnalysisHistory.objects.filter(success=True).count()
            context.update({
                'total_public_analyses': total_analyses,
                'platforms_stats': self.get_platform_stats(),
                'recent_successful': AnalysisHistory.objects.filter(
                    success=True
                ).order_by('-created_at')[:5]
            })
            
            # ✅ PLANTILLAS EXITOSAS
            try:
                templates = MarketingTemplate.objects.filter(
                    success_rate__gte=70
                ).order_by('-times_used')[:6]
                context['templates'] = templates
            except:
                context['templates'] = []
            
            return render(request, 'analyzer/index.html', context)
            
        except Exception as e:
            logger.error(f"Error in GET request: {str(e)}")
            return render(request, 'analyzer/index.html', {
                'error': 'Error al cargar la página. Intenta recargar.'
            })
    
    def post(self, request):
        """Manejo robusto de análisis"""
        try:
            # ✅ VALIDAR CSRF TOKEN
            if not request.META.get('HTTP_X_CSRFTOKEN') and 'csrfmiddlewaretoken' not in request.POST:
                return JsonResponse({
                    'success': False,
                    'error': 'Token CSRF faltante'
                }, status=403)
            
            # ✅ DETERMINAR TIPO DE ANÁLISIS
            analysis_type = request.POST.get('analysis_type', 'basic').lower()
            logger.info(f"[PROCESSING] Procesando análisis tipo: {analysis_type}")
            
            # ✅ VALIDACIONES BÁSICAS
            if not request.POST.get('api_key'):
                return JsonResponse({
                    'success': False,
                    'error': 'API Key de Gemini es requerida'
                })
            
            # ✅ DIRIGIR AL MÉTODO CORRECTO
            if analysis_type in ['competitive', 'competitor']:
                return self.competitive_analysis(request)
            else:
                return self.basic_analysis(request)
                
        except Exception as e:
            logger.error(f"Error in POST: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': f'Error al procesar solicitud: {str(e)}'
            }, status=500)
    
    def basic_analysis(self, request):
        """Análisis básico mejorado"""
        try:
            # ✅ EXTRAER Y VALIDAR DATOS
            data = self.extract_form_data(request, 'basic')
            validation_error = self.validate_basic_data(data)
            if validation_error:
                return JsonResponse({'success': False, 'error': validation_error})
            
            logger.info(f"[ANALYZING] Analizando: {data['product_url']}")
            
            # ✅ SCRAPING CON TIMEOUT Y RETRY
            product_info = self.safe_scrape_product(data['product_url'])
            if not product_info['success']:
                return JsonResponse({
                    'success': False,
                    'error': f'No se pudo analizar el producto: {product_info.get("error", "Error desconocido")}'
                })
            
            # ✅ GENERAR PROMPT INTELIGENTE
            prompt = self.build_basic_prompt(product_info['data'], data)
            
            # ✅ LLAMADA A IA CON MANEJO DE ERRORES
            ai_response = self.safe_ai_call(prompt, data['api_key'])
            if not ai_response['success']:
                return JsonResponse({
                    'success': False,
                    'error': ai_response['error']
                })
            
            # ✅ GUARDAR EN BD CON MANEJO DE ERRORES
            analysis = self.save_analysis(request.user, product_info['data'], data, 'basic', ai_response['response'])
            
            # ✅ RESPUESTA EXITOSA
            return JsonResponse({
                'success': True,
                'analysis_id': analysis.id,
                'response': ai_response['response'],
                'product': product_info['data'],
                'message': '¡Análisis completado exitosamente!'
            })
            
        except Exception as e:
            logger.error(f"Error in basic_analysis: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': 'Error interno del servidor. Intenta nuevamente.'
            }, status=500)
    
    def competitive_analysis(self, request):
        """Análisis competitivo mejorado"""
        try:
            # ✅ EXTRAER DATOS
            data = self.extract_form_data(request, 'competitive')
            validation_error = self.validate_competitive_data(data)
            if validation_error:
                return JsonResponse({'success': False, 'error': validation_error})
            
            # ✅ PRODUCTO PRINCIPAL
            main_url = data.get('main_product_url') or data.get('product_url')
            logger.info(f"[COMPETITIVE] Análisis competitivo: {main_url}")
            
            main_product = self.safe_scrape_product(main_url)
            if not main_product['success']:
                return JsonResponse({
                    'success': False,
                    'error': 'No se pudo analizar el producto principal'
                })
            
            # ✅ COMPETIDORES (opcional)
            competitors_data = []
            competitor_urls = [data.get(f'competitor_{i}') for i in range(1, 6) if data.get(f'competitor_{i}')]
            
            for url in competitor_urls:
                comp_info = self.safe_scrape_product(url)
                if comp_info['success']:
                    competitors_data.append(comp_info['data'])
            
            logger.info(f"📊 Competidores analizados: {len(competitors_data)}")
            
            # ✅ ANÁLISIS DE PRECIOS
            price_analysis = self.analyze_pricing(main_product['data'], competitors_data)
            
            # ✅ PROMPT COMPETITIVO
            prompt = self.build_competitive_prompt(main_product['data'], competitors_data, data, price_analysis)
            
            # ✅ IA CALL
            ai_response = self.safe_ai_call(prompt, data['api_key'])
            if not ai_response['success']:
                return JsonResponse({
                    'success': False,
                    'error': ai_response['error']
                })
            
            # ✅ GUARDAR ANÁLISIS
            analysis = self.save_analysis(
                user=request.user,
                product_data=main_product['data'],
                form_data=data,
                analysis_type='competitive',
                ai_response=ai_response['response'],
                additional_data={
                    'competitors_analyzed': len(competitors_data),
                    'price_position': price_analysis['position'],
                    'competitors': competitors_data[:3]  # Solo guardar primeros 3
                }
            )
            
            return JsonResponse({
                'success': True,
                'analysis_id': analysis.id,
                'response': ai_response['response'],
                'main_product': main_product['data'],
                'competitors_analyzed': len(competitors_data),
                'pricing_analysis': price_analysis
            })
            
        except Exception as e:
            logger.error(f"Error in competitive_analysis: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': 'Error en análisis competitivo. Intenta nuevamente.'
            }, status=500)
    
    # ✅ MÉTODOS AUXILIARES
    
    def extract_form_data(self, request, analysis_type):
        """Extrae datos del formulario de forma segura"""
        data = {
            'product_url': request.POST.get('product_url', '').strip(),
            'platform': request.POST.get('platform', 'tiktok'),
            'target_audience': request.POST.get('target_audience', '').strip(),
            'additional_context': request.POST.get('additional_context', '').strip(),
            'campaign_goal': request.POST.get('campaign_goal', 'conversions'),
            'budget': request.POST.get('budget', 'medium'),
            'tone': request.POST.get('tone', 'professional'),
            'api_key': request.POST.get('api_key', '').strip(),
        }
        
        if analysis_type == 'competitive':
            data['main_product_url'] = request.POST.get('main_product_url', '').strip()
            for i in range(1, 6):
                data[f'competitor_{i}'] = request.POST.get(f'competitor_{i}', '').strip()
        
        return data
    
    def validate_basic_data(self, data):
        """Valida datos para análisis básico"""
        if not data['product_url']:
            return 'URL del producto es requerida'
        if not data['target_audience']:
            return 'Público objetivo es requerido'
        if not data['api_key']:
            return 'API Key de Gemini es requerida'
        return None
    
    def validate_competitive_data(self, data):
        """Valida datos para análisis competitivo"""
        main_url = data.get('main_product_url') or data.get('product_url')
        if not main_url:
            return 'URL del producto principal es requerida'
        if not data['target_audience']:
            return 'Público objetivo es requerido'
        if not data['api_key']:
            return 'API Key de Gemini es requerida'
        return None
    
    def safe_scrape_product(self, url, max_retries=2):
        """Scraping seguro con reintentos"""
        for attempt in range(max_retries + 1):
            try:
                result = scrape_product_info(url)
                if result['success']:
                    return result
                if attempt == max_retries:
                    return result
            except Exception as e:
                if attempt == max_retries:
                    return {
                        'success': False,
                        'error': f'Error al procesar la URL: {str(e)}'
                    }
        return {'success': False, 'error': 'Error desconocido'}
    
    def safe_ai_call(self, prompt, api_key):
        """Llamada segura a la IA"""
        try:
            response = generate_strategy(prompt, api_key)
            if response and isinstance(response, dict) and response.get('success'):
                return {'success': True, 'response': response.get('response', '')}
            else:
                return {'success': False, 'error': 'Respuesta de IA vacía o inválida'}
        except Exception as e:
            logger.error(f"AI call error: {str(e)}")
            return {'success': False, 'error': 'Error en la generación con IA. Verifica tu API Key.'}
    
    
    
    
    def analyze_pricing(self, main_product, competitors_data):
        """Análisis inteligente de precios"""
        try:
            # Extraer precio principal
            main_price_str = main_product.get('price', '0')
            main_price = self.extract_price(main_price_str)
            
            # Extraer precios de competidores
            competitor_prices = []
            for comp in competitors_data:
                price = self.extract_price(comp.get('price', '0'))
                if price > 0:
                    competitor_prices.append(price)
            
            if not competitor_prices:
                return {'position': 'sin_competencia', 'avg_competitor_price': 0, 'main_price': main_price}
            
            avg_price = sum(competitor_prices) / len(competitor_prices)
            
            if main_price > avg_price * 1.2:
                position = 'premium'
            elif main_price < avg_price * 0.8:
                position = 'economico'
            else:
                position = 'competitivo'
            
            return {
                'position': position,
                'main_price': main_price,
                'avg_competitor_price': avg_price,
                'competitor_prices': competitor_prices
            }
            
        except Exception as e:
            logger.error(f"Pricing analysis error: {str(e)}")
            return {'position': 'unknown', 'main_price': 0, 'avg_competitor_price': 0}
    
    def extract_price(self, price_str):
        """Extrae precio numérico de string"""
        try:
            import re
            # Buscar números con decimales
            matches = re.findall(r'[\d,]+\.?\d*', str(price_str))
            if matches:
                price_clean = matches[0].replace(',', '')
                return float(price_clean)
        except:
            pass
        return 0
    
    def build_basic_prompt(self, product_data, form_data):
        """Construye prompt inteligente para análisis básico"""
        return f"""
        Actúa como un experto en marketing de afiliados con 10+ años de experiencia y genera una estrategia ESPECÍFICA y ACTIONABLE.
        
        PRODUCTO A PROMOCIONAR:
        - Título: {product_data.get('title', 'Producto')}
        - Precio: {product_data.get('price', 'No especificado')}
        - Descripción: {product_data.get('description', 'No disponible')[:500]}
        
        CONFIGURACIÓN DE CAMPAÑA:
        - Plataforma Principal: {form_data['platform']}
        - Audiencia Objetivo: {form_data['target_audience']}
        - Objetivo: {form_data['campaign_goal']}
        - Presupuesto: {form_data['budget']}
        - Tono: {form_data['tone']}
        - Contexto Adicional: {form_data['additional_context']}
        
        GENERA UNA ESTRATEGIA COMPLETA CON:
        
        ## 🎯 1. ANÁLISIS DEL PRODUCTO
        - ¿Qué problema resuelve?
        - ¿Cuál es su propuesta de valor única?
        - ¿Por qué alguien lo compraría?
        
        ## 👥 2. ESTRATEGIA DE AUDIENCIA
        - Perfil detallado del cliente ideal
        - Puntos de dolor específicos
        - Motivaciones de compra
        
        ## 📱 3. ESTRATEGIA DE CONTENIDO PARA {form_data['platform'].upper()}
        - 5 ideas específicas de contenido
        - Formato recomendado (video, imagen, carrusel)
        - Frecuencia de publicación óptima
        
        ## 💬 4. MENSAJES CLAVE
        - Hook principal (primera línea que captará atención)
        - 3 beneficios principales a comunicar
        - Call-to-action específico y persuasivo
        
        ## 🔥 5. TÁCTICAS DE CONVERSIÓN
        - Estrategias de urgencia/escasez
        - Ofertas irresistibles
        - Seguimiento post-click
        
        ## 📊 6. HASHTAGS Y KEYWORDS
        - 15 hashtags específicos para {form_data['platform']}
        - Keywords para SEO/búsquedas
        
        ## 📈 7. MÉTRICAS Y OPTIMIZACIÓN
        - KPIs principales a trackear
        - Metas realistas para los primeros 30 días
        - Cómo optimizar basado en resultados
        
        ## 💰 8. ESTRATEGIA DE PRESUPUESTO ({form_data['budget']})
        - Distribución recomendada
        - Cuándo y cómo escalar
        
        Sé MUY específico, usa números exactos y proporciona acciones concretas que se puedan implementar HOY.
        """
    
    def build_competitive_prompt(self, main_product, competitors, form_data, price_analysis):
        """Construye prompt para análisis competitivo"""
        competitors_info = "\n".join([
            f"- {comp.get('title', 'Competidor')}: {comp.get('price', 'N/A')} - {comp.get('description', '')[:100]}"
            for comp in competitors[:5]
        ]) if competitors else "No se proporcionaron competidores específicos"
        
        return f"""
        Actúa como un consultor de competitive intelligence y genera un PLAN DE ATAQUE para dominar tu nicho.
        
        TU PRODUCTO:
        - Título: {main_product.get('title')}
        - Precio: {main_product.get('price')} (Posición: {price_analysis['position']})
        - Descripción: {main_product.get('description', '')[:300]}
        
        COMPETENCIA ANALIZADA:
        {competitors_info}
        
        MERCADO OBJETIVO:
        - Plataforma: {form_data['platform']}
        - Audiencia: {form_data['target_audience']}
        
        GENERA UNA ESTRATEGIA COMPETITIVA:
        
        ## 🎯 ANÁLISIS COMPETITIVO
        ### Ventajas de tu producto vs competencia
        ### Debilidades que debes mejorar
        ### Oportunidades no explotadas
        
        ## ⚔️ ESTRATEGIAS DE DIFERENCIACIÓN
        ### Cómo posicionarte como ÚNICO
        ### Ángulos que la competencia NO usa
        ### Propuesta de valor disruptiva
        
        ## 💰 ESTRATEGIA DE PRECIO ({price_analysis['position']})
        ### Cómo justificar tu precio
        ### Tácticas de valor percibido
        ### Promociones estratégicas
        
        ## 🚀 PLAN DE ATAQUE INMEDIATO
        ### 5 acciones para robar market share
        ### Contenido que supere a la competencia
        ### Tácticas de guerrilla marketing
        
        ## 📊 MONITOREO COMPETITIVO
        ### Qué trackear de la competencia
        ### Cómo reaccionar a sus movimientos
        ### Indicadores de alerta temprana
        
        Sé AGRESIVO y específico. El objetivo es DOMINAR este nicho en los próximos 90 días.
        """
    
    def save_analysis(self, user, product_data, form_data, analysis_type, ai_response, additional_data=None):
        """Guarda análisis en la base de datos"""
        try:
            analysis = AnalysisHistory.objects.create(
                user=user if user.is_authenticated else None,
                product_url=form_data.get('main_product_url') or form_data['product_url'],
                product_title=product_data.get('title', 'Producto'),
                product_price=product_data.get('price'),
                product_description=product_data.get('description'),
                platform=form_data['platform'],
                target_audience=form_data['target_audience'],
                additional_context=form_data['additional_context'],
                campaign_goal=form_data['campaign_goal'],
                budget=form_data['budget'],
                tone=form_data['tone'],
                analysis_type=analysis_type,
                ai_response=ai_response,
                success=True,
                additional_data=additional_data if additional_data else {}
            )
            logger.info(f"[SUCCESS] Analysis saved with ID: {analysis.id}")
            return analysis
        except Exception as e:
            logger.error(f"Error saving analysis: {str(e)}")
            raise
    
    def get_platform_stats(self):
        """Estadísticas por plataforma"""
        try:
            return AnalysisHistory.objects.filter(success=True).values('platform').annotate(
                count=Count('id')
            ).order_by('-count')[:5]
        except:
            return []


# ✅ VISTAS DE HISTORIAL MEJORADAS
class UserHistoryView(View):
    """Vista de historial mejorada"""
    
    def get(self, request):
        if request.user.is_authenticated:
            analyses = AnalysisHistory.objects.filter(
                user=request.user
            ).order_by('-created_at')
            
            # Paginación simple
            page = request.GET.get('page', 1)
            try:
                page = int(page)
            except:
                page = 1
            
            start = (page - 1) * 20
            end = start + 20
            
            context = {
                'analyses': analyses[start:end],
                'is_authenticated': True,
                'user': request.user,
                'total_analyses': analyses.count(),
                'has_next': analyses.count() > end,
                'has_prev': page > 1,
                'current_page': page,
                'next_page': page + 1 if analyses.count() > end else None,
                'prev_page': page - 1 if page > 1 else None,
            }
        else:
            # Mostrar análisis públicos para usuarios no autenticados
            analyses = AnalysisHistory.objects.filter(
                success=True
            ).order_by('-created_at')[:20]
            
            context = {
                'analyses': analyses,
                'is_authenticated': False,
                'total_analyses': analyses.count()
            }
        
        return render(request, 'analyzer/history.html', context)


class PublicHistoryView(View):
    """Vista de historial público mejorada"""
    
    def get(self, request):
        # Filtros opcionales
        platform = request.GET.get('platform')
        analysis_type = request.GET.get('type')
        
        analyses = AnalysisHistory.objects.filter(success=True)
        
        if platform:
            analyses = analyses.filter(platform=platform)
        if analysis_type:
            analyses = analyses.filter(analysis_type=analysis_type)
        
        analyses = analyses.order_by('-created_at')[:30]
        
        # Estadísticas
        platforms = AnalysisHistory.objects.filter(success=True).values_list('platform', flat=True).distinct()
        
        context = {
            'analyses': analyses,
            'is_public': True,
            'total_analyses': analyses.count(),
            'available_platforms': platforms,
            'selected_platform': platform,
            'selected_type': analysis_type,
        }
        
        return render(request, 'analyzer/public_history.html', context)


# ✅ FUNCIÓN DE DESCARGA MEJORADA
def download_pdf(request, analysis_id):
    """
    Descarga PDF de análisis con manejo de errores mejorado
    """
    try:
        # ✅ BUSCAR EL ANÁLISIS
        analysis = get_object_or_404(AnalysisHistory, id=analysis_id)
        
        # ✅ VERIFICAR PERMISOS (opcional)
        if (analysis.user and 
            request.user != analysis.user and 
            not request.user.is_superuser and
            not request.user.is_staff):
            
            logger.warning(f"Intento de acceso no autorizado al PDF {analysis_id} por {request.user}")
            raise Http404("Análisis no encontrado")
        
        # ✅ IMPORTAR EL GENERADOR PDF
        try:
            from .utils.pdf_generator import generate_strategy_pdf
        except ImportError:
            logger.error("No se pudo importar generate_strategy_pdf")
            return HttpResponse(
                "Error: Generador de PDF no disponible", 
                status=500,
                content_type='text/plain'
            )
        
        # ✅ GENERAR PDF
        logger.info(f"Generando PDF para análisis {analysis_id}")
        
        try:
            pdf_content = generate_strategy_pdf(analysis)
        except Exception as pdf_error:
            logger.error(f"Error generando PDF: {str(pdf_error)}")
            return HttpResponse(
                f"Error generando PDF: {str(pdf_error)}", 
                status=500,
                content_type='text/plain'
            )
        
        # ✅ VERIFICAR QUE SE GENERÓ CONTENIDO
        if not pdf_content:
            logger.error(f"PDF vacío para análisis {analysis_id}")
            return HttpResponse(
                "Error: PDF vacío generado", 
                status=500,
                content_type='text/plain'
            )
        
        # ✅ CREAR NOMBRE DE ARCHIVO SEGURO
        safe_title = re.sub(r'[^\w\s-]', '', analysis.product_title or 'estrategia')
        safe_title = re.sub(r'[-\s]+', '_', safe_title)[:30]
        filename = f"estrategia_{safe_title}_{analysis_id}.pdf"
        
        # ✅ CREAR RESPUESTA HTTP
        response = HttpResponse(
            pdf_content,
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = len(pdf_content)
        
        logger.info(f"PDF descargado exitosamente: {filename}")
        return response
        
    except AnalysisHistory.DoesNotExist:
        logger.warning(f"Análisis {analysis_id} no encontrado")
        raise Http404("Análisis no encontrado")
        
    except Exception as e:
        logger.error(f"Error inesperado en download_pdf: {str(e)}", exc_info=True)
        return HttpResponse(
            f"Error inesperado: {str(e)}", 
            status=500,
            content_type='text/plain'
        )


def test_pdf(request):
    """Vista de prueba para verificar que el PDF funciona"""
    try:
        from .utils.pdf_generator import generate_strategy_pdf
        
        # Crear análisis de prueba
        class MockAnalysis:
            def __init__(self):
                self.id = "test-id"
                self.product_title = "Producto de Prueba PDF"
                self.product_price = "$99.99"
                self.platform = "tiktok"
                self.target_audience = "jóvenes 18-25 años"
                self.analysis_type = "basic"
                self.ai_response = """Esta es una estrategia de prueba para verificar el PDF.

## Análisis del Producto
Este producto resuelve el problema de X y tiene gran potencial.

## Estrategia de Contenido
- Video corto mostrando beneficios
- Posts en redes sociales
- Testimonios de usuarios

## Call to Action
¡Compra ahora con descuento especial!

**Hashtags recomendados:** #test #marketing #afiliados"""
                self.created_at = datetime.now()
            
            def get_platform_display(self):
                return "TikTok"
        
        mock_analysis = MockAnalysis()
        pdf_content = generate_strategy_pdf(mock_analysis)
        
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="test_estrategia.pdf"'
        
        return response
        
    except Exception as e:
        return HttpResponse(f"Error en test PDF: {str(e)}", status=500)