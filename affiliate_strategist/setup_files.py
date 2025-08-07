# setup_files.py
# Este script creará todos los archivos necesarios para el proyecto

import os

# Crear directorios si no existen
os.makedirs('analyzer/utils', exist_ok=True)
os.makedirs('analyzer/templates/analyzer', exist_ok=True)

# 1. Crear __init__.py en utils
with open('analyzer/utils/__init__.py', 'w') as f:
    f.write('# This file makes Python treat the directory as a package\n')

# 2. Crear analyzer/urls.py
with open('analyzer/urls.py', 'w') as f:
    f.write('''# analyzer/urls.py

from django.urls import path
from .views import AffiliateStrategistView, history_view

app_name = 'analyzer'

urlpatterns = [
    path('', AffiliateStrategistView.as_view(), name='home'),
    path('history/', history_view, name='history'),  # Opcional
]
''')

# 3. Crear el archivo scraping.py
with open('analyzer/utils/scraping.py', 'w') as f:
    f.write('''# analyzer/utils/scraping.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

def scrape_product_info(url):
    """
    Realiza web scraping de una URL de producto para extraer información básica.
    """
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Estrategia genérica simple
        product_data = {
            'title': '',
            'description': '',
            'price': ''
        }
        
        # Buscar título
        title_element = soup.find('h1')
        if title_element:
            product_data['title'] = title_element.text.strip()
        
        # Buscar precio (patrón simple)
        price_pattern = r'\\$[\\d,]+\\.?\\d*'
        for element in soup.find_all(text=re.compile(price_pattern)):
            match = re.search(price_pattern, element)
            if match:
                product_data['price'] = match.group()
                break
        
        # Buscar descripción
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc and 'content' in meta_desc.attrs:
            product_data['description'] = meta_desc['content']
        
        return {
            'success': True,
            'data': product_data
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error al procesar la página: {str(e)}'
        }
''')

# 4. Crear el archivo ai_integration.py
with open('analyzer/utils/ai_integration.py', 'w') as f:
    f.write('''# analyzer/utils/ai_integration.py

import google.generativeai as genai
from typing import Dict

def generate_strategy(prompt: str, api_key: str) -> Dict:
    """
    Genera una estrategia de marketing usando la API de Gemini.
    """
    
    try:
        # Configurar la API de Gemini
        genai.configure(api_key=api_key)
        
        # Crear el modelo
        model = genai.GenerativeModel('gemini-pro')
        
        # Generar la respuesta
        response = model.generate_content(prompt)
        
        if response.text:
            return {
                'success': True,
                'response': response.text
            }
        else:
            return {
                'success': False,
                'error': 'No se pudo generar una respuesta.'
            }
            
    except Exception as e:
        error_message = str(e)
        
        if "API_KEY_INVALID" in error_message:
            return {
                'success': False,
                'error': 'La API key proporcionada no es válida.'
            }
        else:
            return {
                'success': False,
                'error': f'Error al generar la estrategia: {error_message}'
            }
''')

print("✅ Todos los archivos han sido creados exitosamente!")
print("📂 Estructura de archivos:")
print("   - analyzer/urls.py")
print("   - analyzer/utils/__init__.py")
print("   - analyzer/utils/scraping.py")
print("   - analyzer/utils/ai_integration.py")
print("\n🚀 Ahora puedes ejecutar las migraciones!")