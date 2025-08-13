# analyzer/utils/ai_integration.py

import google.generativeai as genai

def generate_strategy(prompt, api_key):
    """Genera estrategia usando Gemini"""
    try:
        # Configurar API key
        genai.configure(api_key=api_key)
        
        # IMPORTANTE: El modelo gratuito actual es 'gemini-1.5-flash' no 'gemini-pro'
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Generar contenido
        response = model.generate_content(prompt)
        
        if response.text:
            return {
                'success': True,
                'response': response.text
            }
        else:
            return {
                'success': False,
                'error': 'No se pudo generar una respuesta. Intenta de nuevo.'
            }
            
    except Exception as e:
        error_msg = str(e)
        
        # Mensajes de error más específicos
        if '404' in error_msg or 'not found' in error_msg.lower():
            return {
                'success': False,
                'error': 'Modelo no encontrado. Asegúrate de usar "gemini-1.5-flash" y que tu API key sea válida.'
            }
        elif 'API_KEY_INVALID' in error_msg or 'API key not valid' in error_msg:
            return {
                'success': False,
                'error': 'La API key no es válida. Verifica que copiaste correctamente tu key de Google AI Studio.'
            }
        elif 'QUOTA_EXCEEDED' in error_msg or 'quota' in error_msg.lower():
            return {
                'success': False,
                'error': 'Has excedido el límite gratuito. Espera un poco o usa otra API key.'
            }
        else:
            return {
                'success': False,
                'error': f'Error: {error_msg}'
            }


def generate_strategy_cohere(prompt, api_key):
    """
    Alternativa usando Cohere (también gratuito)
    Primero instala: pip install cohere
    """
    try:
        import cohere
        
        # Inicializar cliente
        co = cohere.Client(api_key)
        
        # Generar respuesta
        response = co.generate(
            model='command',  # Modelo gratuito de Cohere
            prompt=prompt,
            max_tokens=1000,
            temperature=0.7
        )
        
        if response.generations:
            return {
                'success': True,
                'response': response.generations[0].text
            }
        else:
            return {
                'success': False,
                'error': 'No se pudo generar respuesta con Cohere.'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Error con Cohere: {str(e)}'
        }


def detect_and_generate(prompt, api_key):
    """
    Detecta automáticamente qué API usar basándose en el formato de la key
    """
    # Las API keys de Google suelen empezar con "AIza"
    if api_key.startswith('AIza'):
        print("Detectado: Google Gemini API")
        return generate_strategy(prompt, api_key)
    else:
        # Intentar primero con Cohere
        print("Intentando con Cohere...")
        result = generate_strategy_cohere(prompt, api_key)
        
        # Si Cohere falla, intentar con Gemini
        if not result['success'] and 'cohere' not in result['error'].lower():
            print("Cohere falló, intentando con Gemini...")
            return generate_strategy(prompt, api_key)
        
        return result