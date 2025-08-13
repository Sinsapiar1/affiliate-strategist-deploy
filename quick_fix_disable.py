# quick_fix_disable.py
# SOLUCIÓN RÁPIDA: Deshabilita la funcionalidad problemática

import os
import re

def quick_fix():
    """
    Solución rápida: comenta la línea problemática en el middleware
    """
    print("🚑 SOLUCIÓN DE EMERGENCIA - Deshabilitando funcionalidad problemática...")
    
    # Buscar archivos donde se llama al método problemático
    files_to_check = [
        'analyzer/middleware.py',
        'analyzer/views.py',
        'config/settings.py'
    ]
    
    fixed = False
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar y comentar la línea problemática
            if 'reset_monthly_counter_if_needed' in content:
                print(f"📝 Encontrada referencia problemática en {file_path}")
                
                # Comentar la línea
                new_content = re.sub(
                    r'(\s*)(.*)reset_monthly_counter_if_needed\(\)',
                    r'\1# \2reset_monthly_counter_if_needed()  # TEMPORALMENTE DESHABILITADO',
                    content
                )
                
                # Escribir el archivo corregido
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"✅ Línea comentada en {file_path}")
                fixed = True
    
    if not fixed:
        print("🤔 No se encontraron referencias problemáticas")
        
        # Agregar método dummy al UserProfile
        models_path = 'analyzer/models.py'
        if os.path.exists(models_path):
            with open(models_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'class UserProfile' in content and 'reset_monthly_counter_if_needed' not in content:
                # Buscar donde agregar el método dummy
                pattern = r'(class UserProfile.*?)(def __str__\(self\):)'
                
                dummy_method = '''
    def reset_monthly_counter_if_needed(self):
        """Método dummy - no hace nada por ahora"""
        pass
    
    '''
                
                new_content = re.sub(
                    pattern,
                    r'\1' + dummy_method + r'\2',
                    content,
                    flags=re.DOTALL
                )
                
                with open(models_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print("✅ Método dummy agregado al UserProfile")
                fixed = True
    
    if fixed:
        print("\n🎉 PROBLEMA TEMPORALMENTE SOLUCIONADO")
        print("✅ Ahora puedes ejecutar: python manage.py runserver")
        print("\n⚠️ NOTA: Esta es una solución temporal.")
        print("📋 Para una solución completa, implementa los métodos del UserProfile correctamente.")
    else:
        print("❌ No se pudo aplicar el fix rápido")
    
    return fixed

if __name__ == "__main__":
    quick_fix()
    