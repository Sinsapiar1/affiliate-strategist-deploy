# analyzer/tests/test_models.py - TESTS DE MODELOS

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import uuid

from analyzer.models import (
    AnalysisHistory, MarketingTemplate, UserProfile, 
    AnalysisFeedback, FavoriteAnalysis, Notification, DailyMetrics
)

class AnalysisHistoryModelTest(TestCase):
    """Tests para el modelo AnalysisHistory"""
    
    def setUp(self):
        """Configuración inicial para tests"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.analysis_data = {
            'user': self.user,
            'product_url': 'https://example.com/product',
            'product_title': 'Test Product',
            'product_price': '$99.99',
            'platform': 'tiktok',
            'target_audience': 'young adults',
            'campaign_goal': 'conversions',
            'analysis_type': 'basic',
            'ai_response': 'Test analysis response',
            'success': True,
        }
    
    def test_create_analysis_history(self):
        """Test crear análisis básico"""
        analysis = AnalysisHistory.objects.create(**self.analysis_data)
        
        self.assertEqual(analysis.user, self.user)
        self.assertEqual(analysis.product_title, 'Test Product')
        self.assertEqual(analysis.platform, 'tiktok')
        self.assertTrue(analysis.success)
        self.assertIsNotNone(analysis.share_token)
        self.assertIsInstance(analysis.id, uuid.UUID)
    
    def test_analysis_str_representation(self):
        """Test representación string del análisis"""
        analysis = AnalysisHistory.objects.create(**self.analysis_data)
        expected_str = f"Test Product - basic ({analysis.created_at.date()})"
        self.assertEqual(str(analysis), expected_str)
    
    def test_is_recent_property(self):
        """Test propiedad is_recent"""
        # Análisis reciente
        recent_analysis = AnalysisHistory.objects.create(**self.analysis_data)
        self.assertTrue(recent_analysis.is_recent)
        
        # Análisis antiguo
        old_analysis = AnalysisHistory.objects.create(**self.analysis_data)
        old_analysis.created_at = timezone.now() - timedelta(days=2)
        old_analysis.save()
        self.assertFalse(old_analysis.is_recent)
    
    def test_age_in_days_property(self):
        """Test propiedad age_in_days"""
        analysis = AnalysisHistory.objects.create(**self.analysis_data)
        self.assertEqual(analysis.age_in_days, 0)  # Creado hoy
    
    def test_get_share_url(self):
        """Test generación de URL para compartir"""
        analysis = AnalysisHistory.objects.create(**self.analysis_data)
        share_url = analysis.get_share_url()
        self.assertTrue(share_url.startswith('/share/'))
        self.assertTrue(analysis.share_token in share_url)
    
    def test_analysis_validation(self):
        """Test validaciones del modelo"""
        # Product rating debe estar entre 0 y 5
        invalid_data = self.analysis_data.copy()
        invalid_data['product_rating'] = 6
        
        analysis = AnalysisHistory(**invalid_data)
        with self.assertRaises(ValidationError):
            analysis.full_clean()
    
    def test_analysis_without_user(self):
        """Test análisis sin usuario (anónimo)"""
        anon_data = self.analysis_data.copy()
        anon_data.pop('user')
        
        analysis = AnalysisHistory.objects.create(**anon_data)
        self.assertIsNone(analysis.user)
        self.assertTrue(analysis.success)

class UserProfileModelTest(TestCase):
    """Tests para el modelo UserProfile"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_profile_creation_signal(self):
        """Test que el perfil se crea automáticamente"""
        # El perfil debería crearse automáticamente via signal
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.plan, 'free')
        self.assertEqual(self.user.profile.analyses_limit_monthly, 5)
    
    def test_analyses_remaining(self):
        """Test cálculo de análisis restantes"""
        profile = self.user.profile
        profile.analyses_this_month = 2
        profile.save()
        
        self.assertEqual(profile.analyses_remaining, 3)
    
    def test_success_rate_calculation(self):
        """Test cálculo de tasa de éxito"""
        profile = self.user.profile
        profile.total_analyses = 10
        profile.successful_analyses = 8
        profile.save()
        
        self.assertEqual(profile.success_rate, 80.0)
    
    def test_can_analyze(self):
        """Test verificación de límites de análisis"""
        profile = self.user.profile
        
        # Usuario gratuito con análisis disponibles
        self.assertTrue(profile.can_analyze())
        
        # Usuario que alcanzó el límite
        profile.analyses_this_month = 5
        profile.save()
        self.assertFalse(profile.can_analyze())
        
        # Usuario premium siempre puede analizar
        profile.plan = 'premium'
        profile.save()
        self.assertTrue(profile.can_analyze())
    
    def test_add_points_and_level(self):
        """Test sistema de puntos y niveles"""
        profile = self.user.profile
        
        # Agregar puntos
        profile.add_points(500)
        self.assertEqual(profile.points, 500)
        self.assertEqual(profile.level, 1)  # Aún nivel 1
        
        # Agregar más puntos para subir nivel
        profile.add_points(600)  # Total: 1100
        self.assertEqual(profile.points, 1100)
        self.assertEqual(profile.level, 2)  # Subió a nivel 2
    
    def test_upgrade_plan(self):
        """Test actualización de plan"""
        profile = self.user.profile
        
        profile.upgrade_plan('pro', 30)
        self.assertEqual(profile.plan, 'pro')
        self.assertEqual(profile.analyses_limit_monthly, 100)
        self.assertIsNotNone(profile.plan_expires)
    
    def test_plan_display_with_emoji(self):
        """Test display del plan con emoji"""
        profile = self.user.profile
        display = profile.get_plan_display_with_emoji()
        self.assertIn('🆓', display)
        self.assertIn('Gratuito', display)

class MarketingTemplateModelTest(TestCase):
    """Tests para plantillas de marketing"""
    
    def setUp(self):
        self.template_data = {
            'name': 'Test Template',
            'platform': 'tiktok',
            'category': 'technology',
            'template': 'Check out [PRODUCTO] for only [PRECIO]!',
            'success_rate': 85.5,
            'times_used': 10,
        }
    
    def test_create_template(self):
        """Test crear plantilla"""
        template = MarketingTemplate.objects.create(**self.template_data)
        
        self.assertEqual(template.name, 'Test Template')
        self.assertEqual(template.platform, 'tiktok')
        self.assertEqual(template.success_rate, 85.5)
        self.assertTrue(template.is_active)
    
    def test_increment_usage(self):
        """Test incrementar uso de plantilla"""
        template = MarketingTemplate.objects.create(**self.template_data)
        initial_usage = template.times_used
        
        template.increment_usage()
        template.refresh_from_db()
        
        self.assertEqual(template.times_used, initial_usage + 1)

# =============================================================================
# analyzer/tests/test_views.py - TESTS DE VISTAS

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.cache import cache
from unittest.mock import patch, MagicMock
import json

class AffiliateStrategistViewTest(TestCase):
    """Tests para la vista principal"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        cache.clear()  # Limpiar cache entre tests
    
    def test_get_homepage_anonymous(self):
        """Test acceso a homepage sin autenticación"""
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Affiliate Strategist Pro')
        self.assertContains(response, 'Iniciar Sesión')
    
    def test_get_homepage_authenticated(self):
        """Test acceso a homepage con usuario autenticado"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
        self.assertContains(response, 'Cerrar Sesión')
    
    @patch('analyzer.views.scrape_product_info')
    @patch('analyzer.views.generate_strategy')
    def test_basic_analysis_success(self, mock_generate, mock_scrape):
        """Test análisis básico exitoso"""
        # Configurar mocks
        mock_scrape.return_value = {
            'success': True,
            'data': {
                'title': 'Test Product',
                'price': '$99.99',
                'description': 'Test description'
            }
        }
        mock_generate.return_value = 'Test AI response'
        
        # Datos del análisis
        analysis_data = {
            'analysis_type': 'basic',
            'product_url': 'https://example.com/product',
            'platform': 'tiktok',
            'target_audience': 'young adults',
            'campaign_goal': 'conversions',
            'budget': 'medium',
            'tone': 'professional',
            'api_key': 'test-api-key',
        }
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/', data=analysis_data)
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar respuesta JSON
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn('analysis_id', response_data)
        self.assertEqual(response_data['response'], 'Test AI response')
    
    @patch('analyzer.views.scrape_product_info')
    def test_basic_analysis_scraping_failure(self, mock_scrape):
        """Test análisis con fallo en scraping"""
        mock_scrape.return_value = {
            'success': False,
            'error': 'Cannot access URL'
        }
        
        analysis_data = {
            'analysis_type': 'basic',
            'product_url': 'https://invalid-url.com/product',
            'platform': 'tiktok',
            'target_audience': 'young adults',
            'api_key': 'test-api-key',
        }
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/', data=analysis_data)
        
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('error', response_data)
    
    def test_analysis_without_api_key(self):
        """Test análisis sin API key"""
        analysis_data = {
            'analysis_type': 'basic',
            'product_url': 'https://example.com/product',
            'platform': 'tiktok',
            'target_audience': 'young adults',
            # Sin api_key
        }
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/', data=analysis_data)
        
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('API Key', response_data['error'])
    
    def test_csrf_protection(self):
        """Test protección CSRF"""
        # Request sin CSRF token
        client = Client(enforce_csrf_checks=True)
        response = client.post('/', {
            'analysis_type': 'basic',
            'product_url': 'https://example.com/product',
        })
        
        self.assertEqual(response.status_code, 403)

class UserHistoryViewTest(TestCase):
    """Tests para vista de historial"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Crear algunos análisis de prueba
        for i in range(5):
            AnalysisHistory.objects.create(
                user=self.user,
                product_url=f'https://example.com/product{i}',
                product_title=f'Product {i}',
                platform='tiktok',
                target_audience='test audience',
                analysis_type='basic',
                ai_response=f'Test response {i}',
                success=True
            )
    
    def test_history_authenticated_user(self):
        """Test historial para usuario autenticado"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/history/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Product 0')
        self.assertContains(response, 'testuser')
    
    def test_history_anonymous_user(self):
        """Test historial para usuario anónimo"""
        response = self.client.get('/history/')
        
        self.assertEqual(response.status_code, 200)
        # Debería mostrar análisis públicos o mensaje para registrarse
        self.assertContains(response, 'Registrarse')

# =============================================================================
# analyzer/tests/test_auth.py - TESTS DE AUTENTICACIÓN

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class AuthenticationTest(TestCase):
    """Tests del sistema de autenticación"""
    
    def setUp(self):
        self.client = Client()
        self.register_url = '/register/'
        self.login_url = '/login/'
        self.logout_url = '/logout/'
    
    def test_register_new_user(self):
        """Test registro de nuevo usuario"""
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
            'company_name': 'Test Company'
        }
        
        response = self.client.post(self.register_url, data=user_data)
        
        # Debería redireccionar después del registro exitoso
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el usuario fue creado
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertTrue(hasattr(user, 'profile'))
    
    def test_register_duplicate_username(self):
        """Test registro con usuario duplicado"""
        # Crear usuario existente
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass'
        )
        
        # Intentar registrar con mismo username
        user_data = {
            'username': 'existinguser',
            'email': 'different@example.com',
            'password': 'testpass123',
            'password2': 'testpass123'
        }
        
        response = self.client.post(self.register_url, data=user_data)
        
        self.assertEqual(response.status_code, 200)  # Vuelve al formulario
        self.assertContains(response, 'usuario ya existe')
    
    def test_register_password_mismatch(self):
        """Test registro con contraseñas que no coinciden"""
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'differentpass'
        }
        
        response = self.client.post(self.register_url, data=user_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'no coinciden')
    
    def test_login_valid_credentials(self):
        """Test login con credenciales válidas"""
        # Crear usuario
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Intentar login
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data=login_data)
        
        self.assertEqual(response.status_code, 302)  # Redirección
        
        # Verificar que el usuario está autenticado
        response = self.client.get('/')
        self.assertContains(response, 'testuser')
    
    def test_login_with_email(self):
        """Test login usando email en lugar de username"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        login_data = {
            'username': 'test@example.com',  # Usar email
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data=login_data)
        self.assertEqual(response.status_code, 302)
    
    def test_login_invalid_credentials(self):
        """Test login con credenciales inválidas"""
        login_data = {
            'username': 'nonexistent',
            'password': 'wrongpass'
        }
        
        response = self.client.post(self.login_url, data=login_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'incorrectos')
    
    def test_logout(self):
        """Test logout de usuario"""
        # Crear y autenticar usuario
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Logout
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)
        
        # Verificar que ya no está autenticado
        response = self.client.get('/')
        self.assertContains(response, 'Iniciar Sesión')

# =============================================================================
# analyzer/tests/test_utils.py - TESTS DE UTILIDADES

from django.test import TestCase
from unittest.mock import patch, MagicMock
import requests

class ScrapingUtilsTest(TestCase):
    """Tests para utilidades de scraping"""
    
    @patch('requests.get')
    def test_scrape_product_info_success(self, mock_get):
        """Test scraping exitoso"""
        # Mock de respuesta HTML
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '''
        <html>
            <head><title>Test Product - $99.99</title></head>
            <body>
                <h1>Test Product</h1>
                <span class="price">$99.99</span>
                <div class="description">Great product description</div>
            </body>
        </html>
        '''
        mock_get.return_value = mock_response
        
        from analyzer.utils.scraping import scrape_product_info
        result = scrape_product_info('https://example.com/product')
        
        self.assertTrue(result['success'])
        self.assertIn('title', result['data'])
        self.assertIn('price', result['data'])
    
    @patch('requests.get')
    def test_scrape_product_info_failure(self, mock_get):
        """Test scraping con fallo de conexión"""
        mock_get.side_effect = requests.RequestException("Connection error")
        
        from analyzer.utils.scraping import scrape_product_info
        result = scrape_product_info('https://invalid-url.com')
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)

class CacheUtilsTest(TestCase):
    """Tests para sistema de cache"""
    
    def setUp(self):
        cache.clear()
    
    def test_cache_analysis_result(self):
        """Test cacheo de resultado de análisis"""
        from analyzer.cache import CacheManager
        
        analysis_params = {
            'product_url': 'https://example.com/product',
            'platform': 'tiktok',
            'target_audience': 'young adults',
            'analysis_type': 'basic'
        }
        
        result = {'response': 'Test AI response', 'success': True}
        
        # Cachear resultado
        cache_key = CacheManager.cache_analysis_result(analysis_params, result)
        self.assertIsNotNone(cache_key)
        
        # Recuperar de cache
        cached_result = CacheManager.get_cached_analysis(analysis_params)
        self.assertIsNotNone(cached_result)
        self.assertEqual(cached_result['result'], result)
    
    def test_cache_product_info(self):
        """Test cacheo de información de producto"""
        from analyzer.cache import CacheManager
        
        url = 'https://example.com/product'
        product_data = {
            'title': 'Test Product',
            'price': '$99.99',
            'success': True
        }
        
        # Cachear información
        CacheManager.cache_product_info(url, product_data)
        
        # Recuperar de cache
        cached_data = CacheManager.get_cached_product_info(url)
        self.assertEqual(cached_data, product_data)

# =============================================================================
# analyzer/tests/test_api.py - TESTS DE API REST

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.contrib.auth.models import User

class AnalysisAPITest(TestCase):
    """Tests para API de análisis"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
    
    def test_api_authentication_required(self):
        """Test que la API requiere autenticación"""
        url = reverse('api_analyze')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_api_with_token_authentication(self):
        """Test autenticación con token"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        url = reverse('api_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_user_analyses(self):
        """Test obtener análisis del usuario via API"""
        # Crear análisis
        AnalysisHistory.objects.create(
            user=self.user,
            product_url='https://example.com/product',
            product_title='API Test Product',
            platform='tiktok',
            target_audience='test audience',
            analysis_type='basic',
            ai_response='Test response',
            success=True
        )
        
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        url = reverse('analysis-my-analyses')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['product_title'], 'API Test Product')

# =============================================================================
# analyzer/tests/test_performance.py - TESTS DE RENDIMIENTO

from django.test import TestCase, override_settings
from django.test.utils import override_settings
from django.core.cache import cache
from django.db import connection
from django.test.utils import override_settings
import time

class PerformanceTest(TestCase):
    """Tests de rendimiento y optimización"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='perfuser',
            password='testpass123'
        )
        cache.clear()
    
    def test_database_queries_count(self):
        """Test número de queries en homepage"""
        self.client.login(username='perfuser', password='testpass123')
        
        with self.assertNumQueries(5):  # Ajustar según optimizaciones
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
    
    def test_cache_effectiveness(self):
        """Test efectividad del cache"""
        from analyzer.cache import CacheManager
        
        # Primera llamada (miss)
        start_time = time.time()
        CacheManager.get_cached_platform_stats()
        first_call_time = time.time() - start_time
        
        # Segunda llamada (hit)
        start_time = time.time()
        CacheManager.get_cached_platform_stats()
        second_call_time = time.time() - start_time
        
        # La segunda llamada debería ser más rápida
        self.assertLess(second_call_time, first_call_time * 0.5)
    
    @override_settings(DEBUG=True)
    def test_page_load_time(self):
        """Test tiempo de carga de páginas principales"""
        urls_to_test = ['/', '/public-history/', '/upgrade/']
        
        for url in urls_to_test:
            start_time = time.time()
            response = self.client.get(url)
            load_time = time.time() - start_time
            
            self.assertEqual(response.status_code, 200)
            self.assertLess(load_time, 2.0)  # Menos de 2 segundos

# =============================================================================
# conftest.py - CONFIGURACIÓN PARA PYTEST

import pytest
from django.test import Client
from django.contrib.auth.models import User
from analyzer.models import AnalysisHistory, UserProfile

@pytest.fixture
def user():
    """Usuario de prueba"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def authenticated_client(user):
    """Cliente autenticado"""
    client = Client()
    client.login(username='testuser', password='testpass123')
    return client

@pytest.fixture
def sample_analysis(user):
    """Análisis de muestra"""
    return AnalysisHistory.objects.create(
        user=user,
        product_url='https://example.com/product',
        product_title='Test Product',
        platform='tiktok',
        target_audience='test audience',
        analysis_type='basic',
        ai_response='Test response',
        success=True
    )

# =============================================================================
# pytest.ini - CONFIGURACIÓN DE PYTEST

"""
[tool:pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = tests.py test_*.py *_tests.py
python_classes = Test* *Tests
python_functions = test_*
addopts = 
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=analyzer
    --cov-report=html
    --cov-report=term-missing
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
"""
