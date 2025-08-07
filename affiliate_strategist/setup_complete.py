# setup_complete.py
# -*- coding: utf-8 -*-
# Script completo para crear TODOS los archivos necesarios del proyecto

import os

# Asegurar que los directorios existen
os.makedirs('analyzer/utils', exist_ok=True)
os.makedirs('analyzer/templates/analyzer', exist_ok=True)

print("🔧 Creando todos los archivos del proyecto...\n")

# 1. analyzer/__init__.py (si no existe)
if not os.path.exists('analyzer/__init__.py'):
    with open('analyzer/__init__.py', 'w', encoding='utf-8') as f:
        f.write('')
    print("✅ Creado: analyzer/__init__.py")

# 2. analyzer/utils/__init__.py
with open('analyzer/utils/__init__.py', 'w', encoding='utf-8') as f:
    f.write('# This file makes Python treat the directory as a package\n')
print("✅ Creado: analyzer/utils/__init__.py")

# 3. analyzer/urls.py
with open('analyzer/urls.py', 'w', encoding='utf-8') as f:
    f.write('''# analyzer/urls.py

from django.urls import path
from .views import AffiliateStrategistView, history_view

app_name = 'analyzer'

urlpatterns = [
    path('', AffiliateStrategistView.as_view(), name='home'),
    path('history/', history_view, name='history'),  # Opcional
]
''')
print("✅ Creado: analyzer/urls.py")

# 4. analyzer/models.py
with open('analyzer/models.py', 'w', encoding='utf-8') as f:
    f.write('''# analyzer/models.py

from django.db import models
from django.utils import timezone

class AnalysisHistory(models.Model):
    """
    Modelo para guardar el historial de analisis realizados.
    """
    
    # Campos del formulario
    product_url = models.URLField(max_length=500, help_text="URL del producto analizado")
    target_audience = models.TextField(help_text="Descripcion del publico objetivo")
    platform = models.CharField(
        max_length=50,
        choices=[
            ('instagram', 'Instagram'),
            ('tiktok', 'TikTok'),
            ('facebook', 'Facebook'),
            ('blog', 'Blog'),
        ],
        help_text="Plataforma de marketing seleccionada"
    )
    
    # Datos extraidos del scraping
    product_title = models.CharField(max_length=300, blank=True)
    product_description = models.TextField(blank=True)
    product_price = models.CharField(max_length=50, blank=True)
    
    # Resultado de la IA
    ai_response = models.TextField(blank=True, help_text="Respuesta generada por la IA")
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    success = models.BooleanField(default=False, help_text="Si el analisis fue exitoso")
    error_message = models.TextField(blank=True, help_text="Mensaje de error si fallo")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Historial de Analisis"
        verbose_name_plural = "Historiales de Analisis"
    
    def __str__(self):
        return f"{self.product_title or 'Sin titulo'} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
''')
print("✅ Creado: analyzer/models.py")

# 5. analyzer/views.py
with open('analyzer/views.py', 'w', encoding='utf-8') as f:
    f.write('''# analyzer/views.py

from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from .models import AnalysisHistory
from .utils.scraping import scrape_product_info
from .utils.ai_integration import generate_strategy
import json

class AffiliateStrategistView(View):
    """
    Vista principal que maneja tanto GET (mostrar formulario) 
    como POST (procesar analisis)
    """
    
    def get(self, request):
        """
        Muestra el formulario principal
        """
        context = {
            'platforms': [
                ('instagram', 'Instagram'),
                ('tiktok', 'TikTok'),
                ('facebook', 'Facebook'),
                ('blog', 'Blog'),
            ]
        }
        return render(request, 'analyzer/index.html', context)
    
    def post(self, request):
        """
        Procesa el formulario y genera la estrategia
        """
        try:
            # Paso A: Recibir datos del formulario
            product_url = request.POST.get('product_url', '').strip()
            target_audience = request.POST.get('target_audience', '').strip()
            platform = request.POST.get('platform', '').strip()
            api_key = request.POST.get('api_key', '').strip()
            
            # Validacion basica
            if not all([product_url, target_audience, platform, api_key]):
                return JsonResponse({
                    'success': False,
                    'error': 'Por favor completa todos los campos del formulario.'
                })
            
            # Paso B: Realizar Web Scraping
            print(f"Iniciando scraping de: {product_url}")
            scraping_result = scrape_product_info(product_url)
            
            if not scraping_result['success']:
                return JsonResponse({
                    'success': False,
                    'error': f"Error al analizar la pagina: {scraping_result['error']}"
                })
            
            # Extraer datos del scraping
            product_data = scraping_result['data']
            
            # Paso C: Construir el prompt dinamico
            prompt = self.build_prompt(product_data, target_audience, platform)
            
            # Paso D: Conectar con la API de IA
            print("Generando estrategia con IA...")
            ai_result = generate_strategy(prompt, api_key)
            
            if not ai_result['success']:
                return JsonResponse({
                    'success': False,
                    'error': f"Error con la API de IA: {ai_result['error']}"
                })
            
            # Guardar en el historial (opcional)
            analysis = AnalysisHistory.objects.create(
                product_url=product_url,
                target_audience=target_audience,
                platform=platform,
                product_title=product_data.get('title', ''),
                product_description=product_data.get('description', ''),
                product_price=product_data.get('price', ''),
                ai_response=ai_result['response'],
                success=True
            )
            
            # Paso E: Devolver resultados
            return JsonResponse({
                'success': True,
                'response': ai_result['response'],
                'product_info': product_data
            })
            
        except Exception as e:
            print(f"Error inesperado: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f"Error inesperado: {str(e)}"
            })
    
    def build_prompt(self, product_data, target_audience, platform):
        """Construye el prompt para la IA"""
        return f"""Eres un experto estratega en marketing de afiliados. Analiza la siguiente informacion y genera un plan de accion.

**1. Informacion del Producto (extraida de la web):**
- Titulo: {product_data.get('title', 'No disponible')}
- Descripcion: {product_data.get('description', 'No disponible')[:500]}...
- Precio: {product_data.get('price', 'No disponible')}

**2. Contexto de Marketing (proporcionado por el usuario):**
- Publico Objetivo: {target_audience}
- Plataforma Principal: {platform.capitalize()}

**3. Tarea a Realizar:**
Genera la siguiente informacion en formato Markdown:

### Analisis de Necesidades
Basado en el producto y el publico, identifica las 3 necesidades o dolores principales que este producto resuelve.

### Estrategia de Contenido para {platform.capitalize()}
Proporciona 2 ideas de contenido especificas para la plataforma seleccionada. Para cada idea, incluye:
- Un titular llamativo
- Un breve texto (copy) 
- 3 hashtags relevantes

### Angulos de Venta
Sugiere 2 angulos de venta persuasivos para usar en anuncios pagados.

Formato tu respuesta de manera clara y profesional."""


# Vista adicional para ver el historial (opcional)
def history_view(request):
    """
    Muestra el historial de analisis realizados
    """
    analyses = AnalysisHistory.objects.filter(success=True)[:10]
    return render(request, 'analyzer/history.html', {'analyses': analyses})
''')
print("✅ Creado: analyzer/views.py")

# 6. analyzer/utils/scraping.py
with open('analyzer/utils/scraping.py', 'w', encoding='utf-8') as f:
    f.write('''# analyzer/utils/scraping.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

def scrape_product_info(url):
    """
    Realiza web scraping de una URL de producto para extraer informacion basica.
    
    Args:
        url (str): URL del producto a analizar
        
    Returns:
        dict: Diccionario con 'success' (bool), 'data' (dict) o 'error' (str)
    """
    
    try:
        # Configurar headers para parecer un navegador real
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Realizar peticion HTTP
        print(f"Conectando a: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parsear HTML con BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Inicializar datos del producto
        product_data = {
            'title': '',
            'description': '',
            'price': ''
        }
        
        # Estrategia generica para extraer datos
        
        # Titulo: buscar en h1, h2, o meta tags
        title_element = soup.find('h1')
        if not title_element:
            title_element = soup.find('h2')
        if not title_element:
            meta_title = soup.find('meta', {'property': 'og:title'})
            if meta_title and 'content' in meta_title.attrs:
                product_data['title'] = meta_title['content']
        else:
            product_data['title'] = title_element.text.strip()
        
        # Precio: buscar patrones comunes
        price_pattern = r'\\$[\\d,]+\\.?\\d*'
        for element in soup.find_all(text=re.compile(price_pattern)):
            match = re.search(price_pattern, element)
            if match:
                product_data['price'] = match.group()
                break
        
        # Descripcion: buscar en meta tags o parrafos
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc and 'content' in meta_desc.attrs:
            product_data['description'] = meta_desc['content']
        else:
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                if len(p.text.strip()) > 50:
                    product_data['description'] = p.text.strip()[:500]
                    break
        
        # Limpiar datos
        for key in product_data:
            if isinstance(product_data[key], str):
                product_data[key] = ' '.join(product_data[key].split())
        
        # Valores por defecto
        if not product_data['title']:
            product_data['title'] = 'Producto sin titulo'
        if not product_data['description']:
            product_data['description'] = 'Descripcion no disponible'
        if not product_data['price']:
            product_data['price'] = 'Precio no disponible'
        
        return {
            'success': True,
            'data': product_data
        }
        
    except requests.RequestException as e:
        return {
            'success': False,
            'error': f'Error al conectar con la pagina: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Error al procesar la pagina: {str(e)}'
        }
''')
print("✅ Creado: analyzer/utils/scraping.py")

# 7. analyzer/utils/ai_integration.py
with open('analyzer/utils/ai_integration.py', 'w', encoding='utf-8') as f:
    f.write('''# analyzer/utils/ai_integration.py

import google.generativeai as genai
from typing import Dict

def generate_strategy(prompt: str, api_key: str) -> Dict:
    """
    Genera una estrategia de marketing usando la API de Gemini.
    
    Args:
        prompt (str): El prompt completo con la informacion del producto y contexto
        api_key (str): La API key de Gemini proporcionada por el usuario
        
    Returns:
        dict: Diccionario con 'success' (bool), 'response' (str) o 'error' (str)
    """
    
    try:
        # Configurar la API de Gemini con la clave proporcionada
        genai.configure(api_key=api_key)
        
        # Crear el modelo (usando Gemini Pro que es gratuito)
        model = genai.GenerativeModel('gemini-pro')
        
        # Configuracion de generacion
        generation_config = {
            'temperature': 0.7,
            'top_p': 0.9,
            'top_k': 40,
            'max_output_tokens': 2048,
        }
        
        # Generar la respuesta
        print("Enviando prompt a Gemini...")
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        # Extraer el texto de la respuesta
        if response.text:
            return {
                'success': True,
                'response': response.text
            }
        else:
            return {
                'success': False,
                'error': 'No se pudo generar una respuesta. Por favor, intenta nuevamente.'
            }
            
    except Exception as e:
        error_message = str(e)
        
        if "API_KEY_INVALID" in error_message:
            return {
                'success': False,
                'error': 'La API key proporcionada no es valida. Por favor, verifica tu clave de Gemini.'
            }
        elif "QUOTA_EXCEEDED" in error_message:
            return {
                'success': False,
                'error': 'Se ha excedido la cuota de la API. Por favor, verifica tu limite en Google AI Studio.'
            }
        else:
            return {
                'success': False,
                'error': f'Error al generar la estrategia: {error_message}'
            }
''')
print("✅ Creado: analyzer/utils/ai_integration.py")

# 8. config/urls.py
with open('config/urls.py', 'w', encoding='utf-8') as f:
    f.write('''# config/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('analyzer.urls')),  # Incluir las URLs de la app analyzer
]
''')
print("✅ Creado: config/urls.py")

# 9. analyzer/templates/analyzer/index.html (el contenido completo del template)
html_content = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Affiliate Strategist - Herramienta de Marketing de Afiliados</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
            padding-top: 30px;
        }
        
        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .main-card {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: #555;
        }
        
        input[type="text"],
        input[type="url"],
        input[type="password"],
        textarea,
        select {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e1e1e1;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        input:focus,
        textarea:focus,
        select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        textarea {
            min-height: 100px;
            resize: vertical;
        }
        
        .btn-analyze {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 18px;
            border-radius: 30px;
            cursor: pointer;
            font-weight: 600;
            width: 100%;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .btn-analyze:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .btn-analyze:disabled {
            opacity: 0.7;
            cursor: not-allowed;
        }
        
        .results-section {
            margin-top: 40px;
            display: none;
        }
        
        .results-container {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 30px;
            border: 2px solid #e9ecef;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            display: none;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .error-message {
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: none;
        }
        
        .ai-response h3 {
            color: #667eea;
            margin-top: 25px;
            margin-bottom: 15px;
        }
        
        .ai-response ul {
            margin-left: 20px;
            line-height: 1.8;
        }
        
        .ai-response p {
            line-height: 1.6;
            margin-bottom: 10px;
        }
        
        .product-info {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .product-info h4 {
            color: #667eea;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Affiliate Strategist</h1>
            <p>Tu asistente inteligente para estrategias de marketing de afiliados</p>
        </div>
        
        <div class="main-card">
            <form id="analysisForm">
                {% csrf_token %}
                
                <div class="form-group">
                    <label for="product_url">URL del Producto</label>
                    <input type="url" id="product_url" name="product_url" 
                           placeholder="https://www.amazon.com/producto..." required>
                </div>
                
                <div class="form-group">
                    <label for="target_audience">Publico Objetivo</label>
                    <textarea id="target_audience" name="target_audience" 
                              placeholder="Describe tu cliente ideal. Ej: Jovenes gamers de 18 a 25 anos interesados en la alta competicion..."
                              required></textarea>
                </div>
                
                <div class="form-group">
                    <label for="platform">Plataforma de Marketing</label>
                    <select id="platform" name="platform" required>
                        <option value="">Selecciona una plataforma...</option>
                        {% for value, name in platforms %}
                            <option value="{{ value }}">{{ name }}</option>
                        {% endfor %}
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="api_key">API Key de IA (Gemini o Cohere)</label>
                    <input type="password" id="api_key" name="api_key" 
                           placeholder="Tu clave API permanece segura y no se guarda" required>
                    <small style="color: #666;">Tu API key se usa solo para esta sesion y no se almacena.</small>
                </div>
                
                <button type="submit" class="btn-analyze" id="analyzeBtn">
                    Analizar y Crear Estrategia
                </button>
            </form>
            
            <div class="error-message" id="errorMessage"></div>
            
            <div class="loading" id="loadingSection">
                <div class="spinner"></div>
                <p>Analizando producto y generando estrategia...</p>
            </div>
            
            <div class="results-section" id="resultsSection">
                <h2 style="margin-bottom: 20px;">Estrategia Generada</h2>
                <div class="results-container">
                    <div class="product-info" id="productInfo"></div>
                    <div class="ai-response" id="aiResponse"></div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        document.getElementById('analysisForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            document.getElementById('errorMessage').style.display = 'none';
            document.getElementById('resultsSection').style.display = 'none';
            document.getElementById('loadingSection').style.display = 'block';
            document.getElementById('analyzeBtn').disabled = true;
            
            const formData = new FormData(e.target);
            
            try {
                const response = await fetch('', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    if (data.product_info) {
                        const productHtml = `
                            <h4>Informacion del Producto</h4>
                            <p><strong>Titulo:</strong> ${data.product_info.title || 'No disponible'}</p>
                            <p><strong>Precio:</strong> ${data.product_info.price || 'No disponible'}</p>
                        `;
                        document.getElementById('productInfo').innerHTML = productHtml;
                    }
                    
                    let aiHtml = data.response
                        .replace(/### (.*)/g, '<h3>$1</h3>')
                        .replace(/## (.*)/g, '<h3>$1</h3>')
                        .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
                        .replace(/- (.*)/g, '<li>$1</li>')
                        .replace(/\\n\\n/g, '</p><p>')
                        .replace(/(<li>.*<\\/li>)/s, '<ul>$1</ul>');
                    
                    document.getElementById('aiResponse').innerHTML = `<p>${aiHtml}</p>`;
                    document.getElementById('resultsSection').style.display = 'block';
                } else {
                    document.getElementById('errorMessage').textContent = data.error;
                    document.getElementById('errorMessage').style.display = 'block';
                }
            } catch (error) {
                document.getElementById('errorMessage').textContent = 
                    'Error de conexion. Por favor, intenta nuevamente.';
                document.getElementById('errorMessage').style.display = 'block';
            } finally {
                document.getElementById('loadingSection').style.display = 'none';
                document.getElementById('analyzeBtn').disabled = false;
            }
        });
    </script>
</body>
</html>'''

with open('analyzer/templates/analyzer/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
print("✅ Creado: analyzer/templates/analyzer/index.html")

print("\n✨ ¡Todos los archivos han sido creados exitosamente!")
print("\n📋 Próximos pasos:")
print("1. Asegúrate de que 'analyzer' esté en INSTALLED_APPS en config/settings.py")
print("2. Ejecuta: python manage.py makemigrations")
print("3. Ejecuta: python manage.py migrate")
print("4. Ejecuta: python manage.py runserver")
print("\n🚀 ¡Tu aplicación estará lista en http://127.0.0.1:8000/")