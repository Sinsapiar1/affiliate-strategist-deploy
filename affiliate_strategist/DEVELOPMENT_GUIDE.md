### **DOCUMENTO 3: DEVELOPMENT_GUIDE.md**

```markdown
# 🛠️ GUÍA DE DESARROLLO - Affiliate Strategist Pro

## 📋 Tabla de Contenidos

1. [Configuración del Entorno](#configuración-del-entorno)
2. [Comandos Esenciales](#comandos-esenciales)
3. [Cómo Agregar Nuevas Funcionalidades](#cómo-agregar-nuevas-funcionalidades)
4. [Mejoras Pendientes (Roadmap)](#mejoras-pendientes)
5. [Testing y Debugging](#testing-y-debugging)
6. [Deployment](#deployment)

## 🔧 Configuración del Entorno

### Requisitos Previos

- Python 3.11+
- pip y venv
- Git
- API Key de Google Gemini

### Setup Inicial

```bash
# 1. Clonar y entrar al proyecto
git clone [url-del-repo]
cd affiliate-strategist

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar Django
python manage.py migrate
python manage.py load_templates
python manage.py createsuperuser  # Opcional: para admin

# 5. Ejecutar
python manage.py runserver
Variables de Entorno (.env)
env# Crear archivo .env en la raíz
SECRET_KEY=tu-clave-secreta-super-segura
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
GEMINI_API_KEY=AIza...  # Opcional, usuarios la ingresan
📝 Comandos Esenciales
Django Básicos
bash# Servidor de desarrollo
python manage.py runserver

# Migraciones
python manage.py makemigrations
python manage.py migrate

# Shell interactivo
python manage.py shell

# Cargar plantillas iniciales
python manage.py load_templates

# Limpiar sesiones
python manage.py clearsessions

# Verificar problemas
python manage.py check
python manage.py check --deploy  # Para producción
Git Workflow
bash# Crear feature branch
git checkout -b feature/nombre-funcionalidad

# Commits semánticos
git commit -m "feat: agregar dashboard analytics"
git commit -m "fix: corregir timeout en scraping"
git commit -m "docs: actualizar README"
git commit -m "style: formatear código PEP8"
git commit -m "refactor: simplificar lógica PDF"
git commit -m "test: agregar tests competencia"

# Merge a main
git checkout main
git merge feature/nombre-funcionalidad
git push origin main
🚀 Cómo Agregar Nuevas Funcionalidades
REGLA DE ORO: No Romper lo Existente
Antes de cualquier cambio:

✅ Hacer backup/branch
✅ Entender el flujo actual
✅ Testear en desarrollo
✅ Documentar cambios

Ejemplo: Agregar Nueva Plataforma de Marketing
1. Actualizar el Modelo (si necesario)
python# analyzer/models.py
PLATFORM_CHOICES = [
    ('instagram', 'Instagram'),
    ('tiktok', 'TikTok'),
    ('pinterest', 'Pinterest'),  # NUEVA
    # ...
]
2. Agregar en el Template
html<!-- analyzer/templates/analyzer/index.html -->
<select id="platform" name="platform">
    <option value="instagram">Instagram</option>
    <option value="tiktok">TikTok</option>
    <option value="pinterest">Pinterest</option>  <!-- NUEVA -->
</select>
3. Actualizar Prompt de IA
python# analyzer/utils/ai_integration.py
PLATFORM_PROMPTS = {
    'instagram': '...',
    'tiktok': '...',
    'pinterest': """  # NUEVO
    Genera estrategia para Pinterest:
    - Pines visuales atractivos
    - Boards temáticos
    - SEO de Pinterest
    """
}
4. Migrar y Testear
bashpython manage.py makemigrations
python manage.py migrate
python manage.py runserver
# Testear manualmente la nueva plataforma
Ejemplo: Agregar Cache para Mejorar Performance
python# analyzer/views.py
from django.core.cache import cache
import hashlib

def basic_analysis(self, request):
    # Generar clave única
    cache_key = hashlib.md5(
        f"{request.POST.get('product_url')}_{request.POST.get('platform')}"
        .encode()
    ).hexdigest()
    
    # Verificar cache
    cached = cache.get(cache_key)
    if cached:
        return JsonResponse({**cached, 'from_cache': True})
    
    # Si no está en cache, generar
    result = self.generate_analysis(request)
    
    # Guardar en cache por 1 hora
    cache.set(cache_key, result, 3600)
    
    return JsonResponse(result)
📊 Mejoras Pendientes (Roadmap)
🔴 PRIORIDAD ALTA (Próximas 2 semanas)
1. Dashboard de Analytics
Tiempo: 4-5 horas
Impacto: ⭐⭐⭐⭐
python# analyzer/views.py
class DashboardView(View):
    def get(self, request):
        # Estadísticas generales
        total_analyses = AnalysisHistory.objects.count()
        
        # Por plataforma
        platform_stats = AnalysisHistory.objects.values('platform').annotate(
            count=Count('id')
        )
        
        # Gráficos con Chart.js
        return render(request, 'analyzer/dashboard.html', context)
2. Sistema de Usuarios Básico
Tiempo: 1 día
Impacto: ⭐⭐⭐⭐⭐ (Monetización)
python# Agregar django.contrib.auth
# Crear modelo UserProfile con límites
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.CharField(choices=[('free', 'Free'), ('pro', 'Pro')])
    analyses_count = models.IntegerField(default=0)
    analyses_limit = models.IntegerField(default=5)
🟡 PRIORIDAD MEDIA (Próximo mes)
3. Análisis Avanzado (Completar Tab)
Agregar al análisis actual:

Análisis psicológico del buyer
Customer journey completo
10 variantes de copy para A/B test
Script de video 60 segundos
Email sequence 5 correos

4. Análisis en Lote
Para usuarios Pro:

Subir CSV con productos
Análisis masivo
Export a Excel

5. API REST
python# analyzer/api.py
from rest_framework import viewsets

class AnalysisViewSet(viewsets.ModelViewSet):
    """
    API para integraciones externas
    """
    queryset = AnalysisHistory.objects.all()
    serializer_class = AnalysisSerializer
    authentication_classes = [TokenAuthentication]
🟢 PRIORIDAD BAJA (Futuro)
6. Cache Inteligente

Redis para cache
CDN para estáticos
Optimización queries

7. Notificaciones

Email cuando termine análisis largo
Webhook para integraciones

8. App Móvil

React Native o Flutter
API REST requerida primero

🧪 Testing y Debugging
Tests Básicos
python# analyzer/tests.py
from django.test import TestCase, Client
from .models import AnalysisHistory

class AnalyzerTestCase(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_homepage_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_basic_analysis(self):
        data = {
            'product_url': 'https://test.com/product',
            'platform': 'instagram',
            'target_audience': 'Test audience',
            'api_key': 'test-key'
        }
        response = self.client.post('/', data)
        self.assertEqual(response.status_code, 200)
Debugging Common Issues
python# Shell debugging
python manage.py shell

from analyzer.models import AnalysisHistory
from django.db.models import Count

# Ver últimos errores
AnalysisHistory.objects.filter(
    success=False
).values('error_message').annotate(
    count=Count('id')
)

# Limpiar análisis fallidos antiguos
from datetime import datetime, timedelta
old = datetime.now() - timedelta(days=30)
AnalysisHistory.objects.filter(
    success=False,
    created_at__lt=old
).delete()
Logging
python# analyzer/views.py
import logging
logger = logging.getLogger(__name__)

def basic_analysis(self, request):
    logger.info(f"Iniciando análisis para: {request.POST.get('product_url')}")
    try:
        # código
    except Exception as e:
        logger.error(f"Error en análisis: {e}", exc_info=True)
🚀 Deployment
Checklist Pre-Deployment
bash# 1. Tests
python manage.py test

# 2. Check deployment
python manage.py check --deploy

# 3. Collectstatic
python manage.py collectstatic --noinput

# 4. Variables de entorno
export DEBUG=False
export SECRET_KEY=produccion-key-segura
export ALLOWED_HOSTS=tudominio.com

# 5. Base de datos producción
export DATABASE_URL=postgres://user:pass@host:5432/dbname
Configuración Producción
python# config/settings_prod.py
from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['tudominio.com']

# Seguridad
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Base de datos
DATABASES = {
    'default': dj_database_url.config()
}

# Cache con Redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
Deploy con Gunicorn
bash# Instalar
pip install gunicorn

# Ejecutar
gunicorn config.wsgi:application --bind 0.0.0.0:8000

# Con supervisor
[program:affiliate_strategist]
command=/path/to/venv/bin/gunicorn config.wsgi:application
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
💡 Tips y Mejores Prácticas
Performance

Usa select_related/prefetch_related para evitar N+1 queries
Pagina resultados cuando muestres listas largas
Cache agresivamente resultados que no cambien
Optimiza imágenes y usa lazy loading

Seguridad

Nunca commitees API keys o secrets
Valida todo input del usuario
Usa HTTPS siempre en producción
Actualiza dependencias regularmente

Código Limpio

Sigue PEP 8 para Python
Documenta funciones complejas
Usa nombres descriptivos de variables
Evita duplicación - DRY principle
Testea cambios importantes

📞 Soporte y Contacto

Issues: GitHub Issues
Email: tu@email.com
Documentación: Este archivo + README.md + TECHNICAL_DOCUMENTATION.md


Última actualización: Agosto 2024
Versión actual: v1.3
Estado: Producción