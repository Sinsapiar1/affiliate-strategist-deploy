# verify_setup.py
# Script para verificar que todo está correctamente configurado

import os
import sys

print("🔍 Verificando la configuración del proyecto...\n")

# Lista de archivos necesarios
required_files = {
    'config/settings.py': 'Configuración principal de Django',
    'config/urls.py': 'URLs principales del proyecto',
    'analyzer/__init__.py': 'Inicializador del paquete analyzer',
    'analyzer/apps.py': 'Configuración de la app',
    'analyzer/models.py': 'Modelos de la base de datos',
    'analyzer/views.py': 'Vistas de la aplicación',
    'analyzer/urls.py': 'URLs de la app analyzer',
    'analyzer/utils/__init__.py': 'Inicializador del paquete utils',
    'analyzer/utils/scraping.py': 'Funciones de web scraping',
    'analyzer/utils/ai_integration.py': 'Integración con IA',
    'analyzer/templates/analyzer/index.html': 'Template principal'
}

all_good = True
missing_files = []

# Verificar cada archivo
for file_path, description in required_files.items():
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        if size > 0:
            print(f"✅ {file_path} ({size} bytes) - {description}")
        else:
            print(f"⚠️  {file_path} (VACÍO) - {description}")
            all_good = False
            missing_files.append(file_path)
    else:
        print(f"❌ {file_path} (NO ENCONTRADO) - {description}")
        all_good = False
        missing_files.append(file_path)

# Verificar la configuración de settings.py
print("\n📋 Verificando configuración...")
try:
    with open('config/settings.py', 'r', encoding='utf-8') as f:
        settings_content = f.read()
        if "'analyzer'" in settings_content or '"analyzer"' in settings_content:
            print("✅ La app 'analyzer' está en INSTALLED_APPS")
        else:
            print("❌ La app 'analyzer' NO está en INSTALLED_APPS")
            print("   Por favor, añade 'analyzer' a la lista INSTALLED_APPS en config/settings.py")
            all_good = False
except Exception as e:
    print(f"❌ Error al leer settings.py: {e}")
    all_good = False

# Verificar imports
print("\n🔧 Verificando imports...")
try:
    # Agregar el directorio actual al path de Python
    sys.path.insert(0, os.getcwd())
    
    # Intentar importar los módulos
    try:
        import analyzer.urls
        print("✅ analyzer.urls se puede importar correctamente")
    except ImportError as e:
        print(f"❌ Error al importar analyzer.urls: {e}")
        all_good = False
    
    try:
        import analyzer.views
        print("✅ analyzer.views se puede importar correctamente")
    except ImportError as e:
        print(f"❌ Error al importar analyzer.views: {e}")
        all_good = False
        
except Exception as e:
    print(f"❌ Error general al verificar imports: {e}")
    all_good = False

# Resumen final
print("\n" + "="*50)
if all_good:
    print("✨ ¡Todo está correctamente configurado!")
    print("\nPróximos pasos:")
    print("1. python manage.py makemigrations")
    print("2. python manage.py migrate")
    print("3. python manage.py runserver")
else:
    print("⚠️  Hay problemas que resolver:")
    if missing_files:
        print(f"\nArchivos faltantes o vacíos: {', '.join(missing_files)}")
        print("Ejecuta: python setup_complete.py")
    print("\nSi el problema persiste, revisa los mensajes de error arriba.")