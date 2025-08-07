# test_encoding.py
# Script para verificar problemas de codificación

import os

print("🔍 Verificando codificación de archivos...\n")

files_to_check = [
    'analyzer/utils/scraping.py',
    'analyzer/utils/ai_integration.py',
    'analyzer/views.py',
    'analyzer/models.py'
]

for file_path in files_to_check:
    if os.path.exists(file_path):
        try:
            # Intentar leer con UTF-8
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"✅ {file_path} - Codificación UTF-8 correcta ({len(content)} caracteres)")
        except UnicodeDecodeError as e:
            print(f"❌ {file_path} - Error de codificación: {e}")
            print(f"   Intentando corregir...")
            
            # Intentar leer con otra codificación y reescribir en UTF-8
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"   ✅ Archivo corregido y guardado en UTF-8")
            except Exception as fix_error:
                print(f"   ❌ No se pudo corregir: {fix_error}")
    else:
        print(f"⚠️  {file_path} - No existe")

print("\n✨ Verificación completada.")
print("Si había errores de codificación, intenta ejecutar las migraciones nuevamente.")
