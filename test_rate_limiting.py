# test_rate_limiting.py - Script para probar que el rate limiting funciona

import requests
import time
import json
from datetime import datetime

class RateLimitTester:
    """Prueba exhaustiva del sistema de rate limiting"""
    
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
    def get_csrf_token(self):
        """Obtiene token CSRF para las peticiones POST"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if 'csrftoken' in self.session.cookies:
                return self.session.cookies['csrftoken']
            
            # Buscar en el HTML si no está en cookies
            import re
            match = re.search(r'csrf_token[\'\"]\s*:\s*[\'\"](.*?)[\'\"]', response.text)
            if match:
                return match.group(1)
                
            return None
        except Exception as e:
            print(f"❌ Error obteniendo CSRF token: {e}")
            return None
    
    def make_analysis_request(self, api_key="test-key-123"):
        """Hace una petición de análisis"""
        csrf_token = self.get_csrf_token()
        
        data = {
            'csrfmiddlewaretoken': csrf_token,
            'analysis_type': 'basic',
            'product_url': 'https://example.com/test-product',
            'platform': 'tiktok',
            'target_audience': 'test audience',
            'campaign_goal': 'conversions',
            'tone': 'professional',
            'api_key': api_key
        }
        
        headers = {
            'X-CSRFToken': csrf_token,
            'Referer': f"{self.base_url}/",
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/",
                data=data,
                headers=headers,
                timeout=10
            )
            
            return {
                'status_code': response.status_code,
                'response': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                'success': response.status_code < 400
            }
        except Exception as e:
            return {
                'status_code': 0,
                'response': str(e),
                'success': False
            }
    
    def test_anonymous_rate_limit(self):
        """Prueba el límite de usuarios anónimos (2 por día)"""
        print("🧪 TESTE: Rate Limiting para Usuarios Anónimos")
        print("=" * 50)
        
        # Limpiar sesión para simular usuario nuevo
        self.session.cookies.clear()
        
        results = []
        
        for i in range(4):  # Intentar 4 análisis (debería bloquear después del 2do)
            print(f"\n📊 Intento {i+1}/4:")
            
            result = self.make_analysis_request()
            results.append(result)
            
            print(f"   Status: {result['status_code']}")
            
            if result['success']:
                print("   ✅ Permitido")
            else:
                if result['status_code'] == 429:
                    print("   🚫 Bloqueado por rate limit (ESPERADO)")
                    if isinstance(result['response'], dict):
                        print(f"   📝 Mensaje: {result['response'].get('error', 'No message')}")
                else:
                    print(f"   ❌ Error: {result['response']}")
            
            # Pequeña pausa entre requests
            time.sleep(1)
        
        # Análisis de resultados
        successful = sum(1 for r in results if r['success'])
        blocked = sum(1 for r in results if r['status_code'] == 429)
        
        print(f"\n📈 RESULTADOS:")
        print(f"   ✅ Exitosos: {successful}")
        print(f"   🚫 Bloqueados: {blocked}")
        
        if successful <= 2 and blocked >= 1:
            print("   🎉 ¡RATE LIMITING FUNCIONA CORRECTAMENTE!")
            return True
        else:
            print("   ⚠️ Rate limiting no está funcionando como esperado")
            return False
    
    def run_tests(self):
        """Ejecuta los tests principales"""
        print("🧪 INICIANDO TESTS DE RATE LIMITING")
        print("=" * 60)
        print(f"🌐 URL Base: {self.base_url}")
        print(f"⏰ Timestamp: {datetime.now()}")
        print()
        
        success = self.test_anonymous_rate_limit()
        
        if success:
            print("\n🎉 ¡TODOS LOS TESTS PASARON!")
        else:
            print("\n⚠️ Hay problemas que revisar")


def main():
    """Función principal"""
    import sys
    
    # Determinar URL base
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        print("🌐 Usando URL por defecto: http://127.0.0.1:8000")
        base_url = "http://127.0.0.1:8000"
    
    # Ejecutar tests
    tester = RateLimitTester(base_url)
    tester.run_tests()


if __name__ == "__main__":
    main()