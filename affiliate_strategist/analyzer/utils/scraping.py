# analyzer/utils/scraping.py

import requests
from bs4 import BeautifulSoup
import re

def scrape_product_info(url):
    """Extrae informacion basica del producto"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        product_data = {
            'title': '',
            'description': '',
            'price': ''
        }
        
        # Buscar titulo
        title = soup.find('h1')
        if title:
            product_data['title'] = title.text.strip()
        else:
            meta_title = soup.find('meta', {'property': 'og:title'})
            if meta_title:
                product_data['title'] = meta_title.get('content', '')
        
        # Buscar precio
        price_pattern = r'\$[\d,]+\.?\d*'
        price_text = soup.find(text=re.compile(price_pattern))
        if price_text:
            match = re.search(price_pattern, price_text)
            if match:
                product_data['price'] = match.group()
        
        # Buscar descripcion
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc:
            product_data['description'] = meta_desc.get('content', '')
        
        # Valores por defecto
        if not product_data['title']:
            product_data['title'] = 'Titulo no encontrado'
        if not product_data['description']:
            product_data['description'] = 'Descripcion no disponible'
        if not product_data['price']:
            product_data['price'] = 'Precio no disponible'
        
        return {
            'success': True,
            'data': product_data
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
