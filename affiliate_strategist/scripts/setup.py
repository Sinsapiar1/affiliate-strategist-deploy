# scripts/setup.py - SCRIPT DE CONFIGURACIÓN INICIAL

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Ejecuta un comando y maneja errores"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completado")
            return True
        else:
            print(f"❌ Error en {description}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error ejecutando {description}: {str(e)}")
        return False

def setup_project():
    """Configuración inicial del proyecto"""
    print("🚀 CONFIGURANDO AFFILIATE STRATEGIST PRO")
    print("=" * 50)
    
    # Crear directorios necesarios
    directories = [
        "logs",
        "media/uploads",
        "static/css",
        "static/js",
        "static/images",
        "staticfiles",
        "analyzer/templates/analyzer/auth",
        "templates/admin"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Creado directorio: {directory}")
    
    # Instalar dependencias
    if not run_command("pip install -r requirements.txt", "Instalando dependencias"):
        print("⚠️ Continúando sin instalar todas las dependencias...")
    
    # Crear migraciones
    run_command("python manage.py makemigrations", "Creando migraciones")
    run_command("python manage.py migrate", "Aplicando migraciones")
    
    # Recopilar archivos estáticos
    run_command("python manage.py collectstatic --noinput", "Recopilando archivos estáticos")
    
    # Crear superusuario (opcional)
    print("\n🔐 ¿Quieres crear un superusuario? (y/n): ", end="")
    if input().lower() == 'y':
        run_command("python manage.py createsuperuser", "Creando superusuario")
    
    # Crear archivo .env
    create_env_file()
    
    print("\n🎉 ¡CONFIGURACIÓN COMPLETADA!")
    print("Para iniciar el servidor ejecuta: python manage.py runserver")

def create_env_file():
    """Crea archivo .env con configuraciones básicas"""
    env_content = """# AFFILIATE STRATEGIST PRO - CONFIGURACIÓN
# Copia este archivo como .env y modifica los valores

# Django
SECRET_KEY=django-insecure-cambiar-en-produccion-12345678901234567890
DEBUG=True

# Base de datos (PostgreSQL para producción)
DB_NAME=affiliate_strategist
DB_USER=postgres
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-password-de-app

# APIs Externas
GEMINI_API_KEY=tu-api-key-de-gemini
OPENAI_API_KEY=tu-api-key-de-openai

# Sentry (Monitoreo de errores)
SENTRY_DSN=

# Redis (Cache)
REDIS_URL=redis://localhost:6379/1
"""
    
    with open('.env.example', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("📄 Creado archivo .env.example")
    print("💡 Copia .env.example a .env y configura tus variables")

if __name__ == "__main__":
    setup_project()


# =============================================================================
# scripts/test_app.py - SCRIPT DE TESTING

import os
import django
import sys
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from analyzer.models import AnalysisHistory, MarketingTemplate
from django.contrib.auth.models import User

def test_database():
    """Prueba la conexión a la base de datos"""
    try:
        user_count = User.objects.count()
        analysis_count = AnalysisHistory.objects.count()
        print(f"✅ Base de datos OK - Usuarios: {user_count}, Análisis: {analysis_count}")
        return True
    except Exception as e:
        print(f"❌ Error de base de datos: {str(e)}")
        return False

def test_scraping():
    """Prueba el sistema de scraping"""
    try:
        from analyzer.utils.scraping import scrape_product_info
        result = scrape_product_info("https://example.com/test")
        print(f"✅ Sistema de scraping funcionando")
        return True
    except Exception as e:
        print(f"❌ Error en scraping: {str(e)}")
        return False

def test_ai_integration():
    """Prueba la integración con IA"""
    try:
        from analyzer.utils.ai_integration import generate_strategy
        # Test con prompt básico
        response = generate_strategy("Test prompt", "test-key")
        print(f"✅ Integración de IA disponible")
        return True
    except Exception as e:
        print(f"⚠️ Integración de IA no disponible: {str(e)}")
        return False

def run_tests():
    """Ejecuta todas las pruebas"""
    print("🧪 EJECUTANDO PRUEBAS DEL SISTEMA")
    print("=" * 40)
    
    tests = [
        ("Base de datos", test_database),
        ("Sistema de scraping", test_scraping),
        ("Integración IA", test_ai_integration),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n🔍 Probando {name}...")
        result = test_func()
        results.append((name, result))
    
    print("\n📊 RESUMEN DE PRUEBAS:")
    print("-" * 30)
    for name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\n🎯 Resultado: {passed}/{total} pruebas pasaron")

if __name__ == "__main__":
    run_tests()


# =============================================================================
# scripts/backup.py - SCRIPT DE BACKUP

import os
import shutil
import datetime
from pathlib import Path
import subprocess

def create_backup():
    """Crea backup completo del proyecto"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"backups/backup_{timestamp}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📦 Creando backup en: {backup_dir}")
    
    # Backup de la base de datos
    try:
        subprocess.run([
            "python", "manage.py", "dumpdata", 
            "--output", str(backup_dir / "database.json")
        ], check=True)
        print("✅ Database backup creado")
    except:
        print("⚠️ Error creando database backup")
    
    # Backup de archivos media
    media_dir = Path("media")
    if media_dir.exists():
        shutil.copytree(media_dir, backup_dir / "media")
        print("✅ Media files backup creado")
    
    # Backup de configuración
    config_files = [".env", "requirements.txt", "config/settings.py"]
    for config_file in config_files:
        if Path(config_file).exists():
            shutil.copy2(config_file, backup_dir)
    print("✅ Configuration backup creado")
    
    print(f"🎉 Backup completado: {backup_dir}")

if __name__ == "__main__":
    create_backup()


# =============================================================================
# scripts/deploy.py - SCRIPT DE DEPLOYMENT

import subprocess
import sys

def deploy_to_production():
    """Script básico de deployment"""
    commands = [
        ("git pull origin main", "Actualizando código"),
        ("pip install -r requirements.txt", "Instalando dependencias"),
        ("python manage.py collectstatic --noinput", "Recopilando estáticos"),
        ("python manage.py migrate", "Aplicando migraciones"),
        ("sudo systemctl restart gunicorn", "Reiniciando servidor"),
        ("sudo systemctl restart nginx", "Reiniciando nginx"),
    ]
    
    print("🚀 INICIANDO DEPLOYMENT A PRODUCCIÓN")
    print("=" * 40)
    
    for command, description in commands:
        print(f"🔄 {description}...")
        try:
            subprocess.run(command.split(), check=True)
            print(f"✅ {description} completado")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error en {description}: {e}")
            print("🛑 Deployment detenido")
            sys.exit(1)
    
    print("🎉 ¡DEPLOYMENT COMPLETADO!")

if __name__ == "__main__":
    deploy_to_production()