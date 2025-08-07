### **DOCUMENTO 2: TECHNICAL_DOCUMENTATION.md**

```markdown
# 📘 DOCUMENTACIÓN TÉCNICA - Affiliate Strategist Pro v1.3

## 📋 Tabla de Contenidos

1. [Información General](#información-general)
2. [Arquitectura](#arquitectura)
3. [Modelos de Datos](#modelos-de-datos)
4. [Vistas y Controladores](#vistas-y-controladores)
5. [Sistema de Templates](#sistema-de-templates)
6. [APIs y Servicios](#apis-y-servicios)
7. [Frontend JavaScript](#frontend-javascript)
8. [Seguridad](#seguridad)

## 🎯 Información General

**Versión:** 1.3  
**Stack:** Django 5.2.4 + Python 3.11 + Google Gemini API + ReportLab  
**Base de Datos:** SQLite (desarrollo) / PostgreSQL (producción recomendado)  
**Estado:** Producción - 100% Funcional

## 🏗️ Arquitectura

### Estructura del Proyecto
affiliate_strategist/
├── config/                    # Configuración Django
│   ├── settings.py           # Configuración principal
│   ├── urls.py              # URLs del proyecto
│   └── wsgi.py
│
├── analyzer/                  # App principal
│   ├── management/
│   │   └── commands/
│   │       └── load_templates.py  # Comando para cargar plantillas
│   │
│   ├── migrations/           # Migraciones de BD
│   │
│   ├── templates/
│   │   └── analyzer/
│   │       ├── index.html   # Template principal (v1.3 sin sobreescritura)
│   │       └── history.html # Historial de análisis
│   │
│   ├── utils/
│   │   ├── scraping.py      # Web scraping inteligente
│   │   ├── ai_integration.py # Integración con Gemini
│   │   └── pdf_generator.py  # Generador PDF con diseños diferenciados
│   │
│   ├── models.py            # Modelos de datos
│   ├── views.py            # Lógica de negocio
│   └── urls.py             # URLs de la app
│
├── static/                  # Archivos estáticos
├── db.sqlite3              # Base de datos
├── requirements.txt        # Dependencias
└── manage.py

## 💾 Modelos de Datos

### AnalysisHistory

```python
class AnalysisHistory(models.Model):
    # Campos principales
    product_url = models.URLField()
    product_title = models.CharField(max_length=500)
    product_price = models.CharField(max_length=100, null=True)
    product_description = models.TextField(null=True)
    
    # Tipo de análisis
    analysis_type = models.CharField(
        max_length=20,
        choices=[
            ('basic', 'Análisis Básico'),
            ('competitive', 'Análisis Competitivo')
        ],
        default='basic'
    )
    
    # Configuración del análisis
    platform = models.CharField(max_length=50)
    target_audience = models.TextField()
    additional_context = models.TextField(null=True)
    
    # Resultados
    ai_response = models.TextField()
    success = models.BooleanField(default=True)
    error_message = models.TextField(null=True)
    
    # Datos competitivos (JSONField)
    competitor_analysis = models.JSONField(null=True)
    main_product_data = models.JSONField(null=True)
    competitors_data = models.JSONField(null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    processing_time = models.FloatField(null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['platform', '-created_at']),
            models.Index(fields=['analysis_type', 'success'])
        ]
MarketingTemplate
pythonclass MarketingTemplate(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    platform = models.CharField(max_length=50)
    template_content = models.JSONField()
    success_rate = models.FloatField(default=70.0)
    times_used = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-success_rate']
🎮 Vistas y Controladores
AffiliateStrategistView (Vista Principal)
pythonclass AffiliateStrategistView(View):
    """
    Maneja análisis básico y competitivo
    v1.3: Sin sobreescritura de resultados
    """
    
    def get(self, request):
        # Carga plantillas para mostrar
        context = {
            'templates': MarketingTemplate.objects.filter(
                success_rate__gte=70
            ).order_by('-times_used')[:6]
        }
        return render(request, 'analyzer/index.html', context)
    
    def post(self, request):
        analysis_type = request.POST.get('analysis_type', 'basic')
        
        if analysis_type == 'competitor':
            return self.competitive_analysis(request)
        else:
            return self.basic_analysis(request)
    
    def basic_analysis(self, request):
        # 1. Scraping del producto
        # 2. Generación con IA
        # 3. Guardar en BD
        # 4. Retornar JSON para frontend
        
    def competitive_analysis(self, request):
        # 1. Scraping múltiple (producto + competidores)
        # 2. Análisis de precios
        # 3. IA especializada en competencia
        # 4. Retornar con datos adicionales
Endpoints Disponibles
MétodoURLDescripciónParámetrosGET/Página principal-POST/Generar análisisanalysis_type, product_url, etcGET/download-pdf/<id>/Descargar PDFtype (opcional)GET/history/Ver historial-
🎨 Sistema de Templates
Gestión de Resultados (v1.3)
javascript// Objeto para almacenar múltiples resultados
let analysisResults = {
    basic: null,
    competitive: null
};

// Función para mostrar tabs solo cuando hay múltiples resultados
function updateResultsTabs() {
    const hasBasic = analysisResults.basic !== null;
    const hasCompetitive = analysisResults.competitive !== null;
    const hasBoth = hasBasic && hasCompetitive;
    
    if (hasBoth) {
        document.getElementById('resultsTabs').style.display = 'flex';
    }
}

// Cambiar entre resultados sin perderlos
function showResultTab(type) {
    document.querySelectorAll('.results-section').forEach(section => {
        section.style.display = 'none';
    });
    
    if (type === 'basic' && analysisResults.basic) {
        document.getElementById('basicResultsSection').style.display = 'block';
    }
}
🔌 APIs y Servicios
Integración con Google Gemini
python# analyzer/utils/ai_integration.py

def generate_with_gemini(prompt, api_key, analysis_type='basic'):
    """
    Genera estrategias usando Gemini 1.5 Flash
    Prompts diferenciados por tipo de análisis
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    if analysis_type == 'competitive':
        # Prompt especializado para competitive intelligence
        enhanced_prompt = COMPETITIVE_PROMPT_TEMPLATE.format(prompt)
    else:
        # Prompt estándar para análisis básico
        enhanced_prompt = BASIC_PROMPT_TEMPLATE.format(prompt)
    
    response = model.generate_content(enhanced_prompt)
    return response.text
Web Scraping Inteligente
python# analyzer/utils/scraping.py

def scrape_product_info(url):
    """
    Extrae información de productos de múltiples plataformas
    Manejo robusto de errores y headers anti-bot
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 ...',
        'Accept-Language': 'es-ES,es;q=0.9'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Lógica de extracción por plataforma
        if 'amazon' in url:
            return extract_amazon_data(soup)
        elif 'shopify' in url:
            return extract_shopify_data(soup)
        # ... más plataformas
        
    except Exception as e:
        logger.error(f"Scraping error: {e}")
        return {'success': False, 'error': str(e)}
📄 Generación de PDFs
PDFs Inteligentes con Diseños Diferenciados
python# analyzer/utils/pdf_generator.py

def generate_strategy_pdf(analysis):
    """
    v1.3: Detecta automáticamente el tipo de análisis
    Genera PDFs con diseños diferenciados
    """
    
    # Detectar tipo de análisis
    is_competitive = (
        hasattr(analysis, 'analysis_type') and 
        analysis.analysis_type == 'competitive'
    )
    
    # Colores según tipo
    if is_competitive:
        primary_color = colors.HexColor('#dc3545')  # Rojo
        title = "Análisis Competitivo"
    else:
        primary_color = colors.HexColor('#667eea')  # Azul
        title = "Estrategia de Marketing"
    
    # Generar PDF con diseño específico
    # ...
🔒 Seguridad
Medidas Implementadas

CSRF Protection - Activado en todos los formularios
API Keys - No se guardan en BD, solo en memoria
Validación - Frontend y backend
Headers Seguros - En scraping y respuestas
Sanitización - Escape de HTML en outputs
Rate Limiting - Preparado para implementar

Headers de Seguridad Recomendados
python# config/settings.py (producción)

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
📊 Métricas de Rendimiento
OperaciónTiempo PromedioNotasScraping básico2-3 segundosUn productoScraping competitivo8-12 segundos3-5 productosGeneración IA básica5-8 segundosGemini 1.5 FlashGeneración IA competitiva10-15 segundosPrompt extendidoGeneración PDF<1 segundoReportLabTotal análisis básico10-15 segundos-Total análisis competitivo25-35 segundos-
⚠️ Problemas Conocidos y Soluciones
✅ RESUELTO en v1.3: Sobreescritura de Resultados
Problema: Los resultados se sobreescribían al cambiar entre análisis
Solución: Sistema de almacenamiento en memoria con tabs dinámicos
⚠️ Pendientes

Límites de API - La API gratuita de Gemini tiene límites
Timeout en scraping - Algunos sitios son lentos
Caracteres especiales en PDF - Algunos emojis no se renderizan

🔄 Versionado
Versión     Cambios Principales
v1.0         MVP - Análisis básico funcional
v1.1         +Plantillas, +PDFs, +UI mejoradav
1.2          +Análisis competitivo completov1.3+Sin sobreescritura, +Tabs funcionales