# deployment/docker/Dockerfile - CONTENEDOR DOCKER

FROM python:3.11-slim-bullseye

# Metadatos
LABEL maintainer="tu-email@example.com"
LABEL description="Affiliate Strategist Pro - Django Application"
LABEL version="1.3"

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.production

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY requirements.txt requirements-prod.txt ./
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copiar código de la aplicación
COPY . .

# Cambiar permisos
RUN chown -R appuser:appuser /app
USER appuser

# Recopilar archivos estáticos
RUN python manage.py collectstatic --noinput --settings=config.settings.production

# Exponer puerto
EXPOSE 8000

# Comando por defecto
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "config.wsgi:application"]

# =============================================================================
# deployment/docker/docker-compose.yml - ORQUESTACIÓN CON DOCKER COMPOSE

version: '3.8'

services:
  # Aplicación Django
  web:
    build: 
      context: ../..
      dockerfile: deployment/docker/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
      - DATABASE_URL=postgresql://affiliate_user:${DB_PASSWORD}@db:5432/affiliate_strategist
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=False
    depends_on:
      - db
      - redis
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - app-network

  # Base de datos PostgreSQL
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=affiliate_strategist
      - POSTGRES_USER=affiliate_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    networks:
      - app-network
    ports:
      - "5432:5432"

  # Redis para cache y sesiones
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - app-network

  # Nginx como proxy reverso
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/sites-available:/etc/nginx/sites-available
      - ./ssl:/etc/nginx/ssl
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - web
    restart: unless-stopped
    networks:
      - app-network

  # Celery para tareas asíncronas
  celery:
    build: 
      context: ../..
      dockerfile: deployment/docker/Dockerfile
    command: celery -A config worker -l info
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
      - DATABASE_URL=postgresql://affiliate_user:${DB_PASSWORD}@db:5432/affiliate_strategist
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - app-network

  # Celery Beat para tareas programadas
  celery-beat:
    build: 
      context: ../..
      dockerfile: deployment/docker/Dockerfile
    command: celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
      - DATABASE_URL=postgresql://affiliate_user:${DB_PASSWORD}@db:5432/affiliate_strategist
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:

networks:
  app-network:
    driver: bridge

# =============================================================================
# deployment/nginx/nginx.conf - CONFIGURACIÓN DE NGINX

user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    # Optimizaciones
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # Compresión
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/m;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

    # Upstream para Django
    upstream django {
        server web:8000;
    }

    # Configuración del servidor
    server {
        listen 80;
        server_name tu-dominio.com www.tu-dominio.com;
        
        # Redireccionar a HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name tu-dominio.com www.tu-dominio.com;

        # Certificados SSL
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_session_timeout 1d;
        ssl_session_cache shared:SSL:50m;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # Root y logs
        root /app;
        access_log /var/log/nginx/access.log main;
        error_log /var/log/nginx/error.log;

        # Archivos estáticos
        location /static/ {
            alias /app/staticfiles/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Archivos media
        location /media/ {
            alias /app/media/;
            expires 1M;
            add_header Cache-Control "public";
        }

        # API con rate limiting
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Login con rate limiting especial
        location /login/ {
            limit_req zone=login burst=10 nodelay;
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Todas las demás requests
        location / {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_redirect off;
        }

        # Health check
        location /health/ {
            access_log off;
            proxy_pass http://django;
        }
    }
}

# =============================================================================
# deployment/scripts/deploy.sh - SCRIPT DE DEPLOYMENT

#!/bin/bash

# deployment/scripts/deploy.sh - Script de deployment automatizado

set -e  # Salir si hay error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones de logging
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuración
APP_NAME="affiliate-strategist-pro"
DOCKER_COMPOSE_FILE="deployment/docker/docker-compose.yml"
BACKUP_DIR="deployment/backups"
DATE=$(date +"%Y%m%d_%H%M%S")

# Funciones
create_backup() {
    log_info "Creando backup de la base de datos..."
    
    mkdir -p $BACKUP_DIR
    
    # Backup de PostgreSQL
    docker-compose -f $DOCKER_COMPOSE_FILE exec -T db pg_dump \
        -U affiliate_user \
        -d affiliate_strategist \
        --no-password \
        > $BACKUP_DIR/db_backup_$DATE.sql
    
    if [ $? -eq 0 ]; then
        log_success "Backup creado: $BACKUP_DIR/db_backup_$DATE.sql"
    else
        log_error "Error creando backup"
        exit 1
    fi
}

update_code() {
    log_info "Actualizando código desde Git..."
    
    # Verificar que estamos en la rama correcta
    CURRENT_BRANCH=$(git branch --show-current)
    if [ "$CURRENT_BRANCH" != "main" ]; then
        log_warning "No estás en la rama main. Rama actual: $CURRENT_BRANCH"
        read -p "¿Continuar? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Pull cambios
    git pull origin main
    
    log_success "Código actualizado"
}

build_images() {
    log_info "Construyendo imágenes Docker..."
    
    docker-compose -f $DOCKER_COMPOSE_FILE build --no-cache
    
    if [ $? -eq 0 ]; then
        log_success "Imágenes construidas"
    else
        log_error "Error construyendo imágenes"
        exit 1
    fi
}

run_migrations() {
    log_info "Ejecutando migraciones..."
    
    docker-compose -f $DOCKER_COMPOSE_FILE exec web python manage.py migrate --noinput
    
    if [ $? -eq 0 ]; then
        log_success "Migraciones completadas"
    else
        log_error "Error en migraciones"
        exit 1
    fi
}

collect_static() {
    log_info "Recopilando archivos estáticos..."
    
    docker-compose -f $DOCKER_COMPOSE_FILE exec web python manage.py collectstatic --noinput
    
    if [ $? -eq 0 ]; then
        log_success "Archivos estáticos recopilados"
    else
        log_error "Error recopilando estáticos"
        exit 1
    fi
}

restart_services() {
    log_info "Reiniciando servicios..."
    
    # Restart con zero-downtime
    docker-compose -f $DOCKER_COMPOSE_FILE up -d --force-recreate web celery celery-beat
    
    # Esperar que los servicios estén listos
    sleep 10
    
    # Verificar que la aplicación responde
    if curl -f -s http://localhost/health/ > /dev/null; then
        log_success "Aplicación reiniciada y funcionando"
    else
        log_error "La aplicación no responde después del reinicio"
        exit 1
    fi
}

cleanup() {
    log_info "Limpiando recursos no utilizados..."
    
    # Limpiar imágenes dangling
    docker image prune -f
    
    # Limpiar backups antiguos (mantener últimos 7)
    find $BACKUP_DIR -name "db_backup_*.sql" -type f -mtime +7 -delete
    
    log_success "Limpieza completada"
}

health_check() {
    log_info "Verificando salud del sistema..."
    
    # Verificar que todos los contenedores están corriendo
    CONTAINERS=(web db redis nginx celery celery-beat)
    
    for container in "${CONTAINERS[@]}"; do
        if docker-compose -f $DOCKER_COMPOSE_FILE ps $container | grep -q "Up"; then
            log_success "$container está corriendo"
        else
            log_error "$container no está corriendo"
            exit 1
        fi
    done
    
    # Verificar conectividad HTTP
    if curl -f -s http://localhost/ > /dev/null; then
        log_success "Aplicación web accesible"
    else
        log_error "Aplicación web no accesible"
        exit 1
    fi
    
    log_success "Sistema saludable"
}

# Función principal de deployment
deploy() {
    log_info "🚀 Iniciando deployment de $APP_NAME"
    
    # Verificar que Docker está corriendo
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker no está corriendo"
        exit 1
    fi
    
    # Verificar que tenemos el archivo de environment
    if [ ! -f ".env" ]; then
        log_error "Archivo .env no encontrado"
        exit 1
    fi
    
    # Pasos del deployment
    create_backup
    update_code
    build_images
    run_migrations
    collect_static
    restart_services
    cleanup
    health_check
    
    log_success "🎉 Deployment completado exitosamente!"
    log_info "La aplicación está disponible en https://tu-dominio.com"
}

# Función de rollback
rollback() {
    log_warning "🔄 Iniciando rollback..."
    
    # Listar backups disponibles
    echo "Backups disponibles:"
    ls -la $BACKUP_DIR/db_backup_*.sql | tail -5
    
    read -p "Ingresa el nombre del backup a restaurar: " BACKUP_FILE
    
    if [ ! -f "$BACKUP_DIR/$BACKUP_FILE" ]; then
        log_error "Backup no encontrado: $BACKUP_DIR/$BACKUP_FILE"
        exit 1
    fi
    
    log_warning "⚠️  ADVERTENCIA: Esto sobrescribirá la base de datos actual"
    read -p "¿Estás seguro? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    
    # Restaurar backup
    log_info "Restaurando backup..."
    docker-compose -f $DOCKER_COMPOSE_FILE exec -T db psql \
        -U affiliate_user \
        -d affiliate_strategist \
        < $BACKUP_DIR/$BACKUP_FILE
    
    restart_services
    
    log_success "Rollback completado"
}

# Función para mostrar logs
show_logs() {
    log_info "📋 Mostrando logs de la aplicación..."
    docker-compose -f $DOCKER_COMPOSE_FILE logs -f --tail=100 web
}

# Función para mostrar estado
show_status() {
    log_info "📊 Estado de los servicios:"
    docker-compose -f $DOCKER_COMPOSE_FILE ps
    
    echo
    log_info "📈 Uso de recursos:"
    docker stats --no-stream
}

# Menú principal
case "${1:-deploy}" in
    deploy)
        deploy
        ;;
    rollback)
        rollback
        ;;
    backup)
        create_backup
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    health)
        health_check
        ;;
    *)
        echo "Uso: $0 {deploy|rollback|backup|logs|status|health}"
        echo
        echo "Comandos disponibles:"
        echo "  deploy   - Deployment completo (por defecto)"
        echo "  rollback - Rollback a backup anterior"
        echo "  backup   - Crear backup de la base de datos"
        echo "  logs     - Mostrar logs de la aplicación"
        echo "  status   - Mostrar estado de servicios"
        echo "  health   - Verificar salud del sistema"
        exit 1
        ;;
esac

# =============================================================================
# deployment/scripts/setup-server.sh - CONFIGURACIÓN INICIAL DEL SERVIDOR

#!/bin/bash

# Script para configurar un servidor Ubuntu 22.04 para Affiliate Strategist Pro

set -e

log_info() {
    echo -e "\033[0;34m[INFO]\033[0m $1"
}

log_success() {
    echo -e "\033[0;32m[SUCCESS]\033[0m $1"
}

log_error() {
    echo -e "\033[0;31m[ERROR]\033[0m $1"
}

# Verificar que somos root o sudo
if [ "$EUID" -ne 0 ]; then
    log_error "Este script debe ejecutarse como root o con sudo"
    exit 1
fi

log_info "🚀 Configurando servidor para Affiliate Strategist Pro"

# Actualizar sistema
log_info "Actualizando sistema..."
apt update && apt upgrade -y

# Instalar dependencias básicas
log_info "Instalando dependencias básicas..."
apt install -y \
    curl \
    wget \
    git \
    ufw \
    fail2ban \
    certbot \
    python3-certbot-nginx \
    htop \
    unzip

# Instalar Docker
log_info "Instalando Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl enable docker
systemctl start docker

# Instalar Docker Compose
log_info "Instalando Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Configurar firewall
log_info "Configurando firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80
ufw allow 443
ufw --force enable

# Configurar fail2ban
log_info "Configurando fail2ban..."
systemctl enable fail2ban
systemctl start fail2ban

# Crear usuario para la aplicación
log_info "Creando usuario para la aplicación..."
useradd -m -s /bin/bash -G docker appuser

# Configurar directorio de la aplicación
log_info "Configurando directorio de aplicación..."
mkdir -p /opt/affiliate-strategist-pro
chown appuser:appuser /opt/affiliate-strategist-pro

# Configurar logs
log_info "Configurando logs..."
mkdir -p /var/log/affiliate-strategist-pro
chown appuser:appuser /var/log/affiliate-strategist-pro

# Configurar logrotate
cat > /etc/logrotate.d/affiliate-strategist-pro << EOF
/var/log/affiliate-strategist-pro/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 appuser appuser
}
EOF

# Configurar monitoreo básico
log_info "Configurando monitoreo básico..."
apt install -y prometheus-node-exporter
systemctl enable prometheus-node-exporter
systemctl start prometheus-node-exporter

# Optimizaciones del sistema
log_info "Aplicando optimizaciones del sistema..."

# Aumentar límites de archivos
cat >> /etc/security/limits.conf << EOF
* soft nofile 65536
* hard nofile 65536
root soft nofile 65536
root hard nofile 65536
EOF

# Optimizaciones de red
cat >> /etc/sysctl.conf << EOF
# Optimizaciones para Affiliate Strategist Pro
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 65536 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_window_scaling = 1
EOF

sysctl -p

log_success "✅ Servidor configurado exitosamente!"
log_info "Siguiente paso: Clonar el repositorio y ejecutar deployment"
log_info "sudo -u appuser git clone https://github.com/tu-usuario/affiliate-strategist-pro.git /opt/affiliate-strategist-pro"

# =============================================================================
# requirements-prod.txt - DEPENDENCIAS DE PRODUCCIÓN

# Archivo: requirements-prod.txt

# Django y extensiones
Django==5.2.4
django-extensions==3.2.3
django-cors-headers==4.3.1
djangorestframework==3.14.0

# Base de datos
psycopg2-binary==2.9.9

# Cache y sesiones
redis==5.0.1
django-redis==5.4.0

# Servidor web
gunicorn==21.2.0
whitenoise==6.6.0

# Tareas asíncronas
celery==5.3.4
django-celery-beat==2.5.0

# Monitoreo y logging
sentry-sdk[django]==1.38.0
prometheus-client==0.18.0

# Web scraping y requests
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
user-agent==0.1.10

# IA y procesamiento
google-generativeai==0.3.2
openai==1.3.7
nltk==3.8.1

# PDFs y archivos
reportlab==4.0.7
Pillow==10.1.0

# Datos y análisis
pandas==2.1.4
numpy==1.24.4

# Validación y seguridad
validators==0.22.0
bleach==6.1.0
cryptography==41.0.7

# Configuración
python-decouple==3.8
python-dotenv==1.0.0

# Fecha y tiempo
python-dateutil==2.8.2
pytz==2023.3

# Utilidades
tqdm==4.66.1
colorama==0.4.6

# =============================================================================
# .env.production - TEMPLATE DE VARIABLES DE ENTORNO PARA PRODUCCIÓN

# .env.production - Template para producción

# Django Configuration
SECRET_KEY=tu-secret-key-super-segura-aqui-256-bits-minimo
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com

# Database Configuration
DATABASE_URL=postgresql://affiliate_user:password@db:5432/affiliate_strategist
DB_PASSWORD=password-super-segura-para-postgresql

# Redis Configuration
REDIS_URL=redis://:password@redis:6379/0
REDIS_PASSWORD=password-super-segura-para-redis

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-password-de-aplicacion

# API Keys
GEMINI_API_KEY=tu-api-key-de-gemini
OPENAI_API_KEY=tu-api-key-de-openai

# Monitoring and Logging
SENTRY_DSN=https://tu-sentry-dsn@sentry.io/proyecto
LOG_LEVEL=INFO

# Security
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https

# Media and Static Files
MEDIA_ROOT=/app/media
STATIC_ROOT=/app/staticfiles

# Celery Configuration
CELERY_BROKER_URL=redis://:password@redis:6379/0
CELERY_RESULT_BACKEND=redis://:password@redis:6379/0

# Feature Flags
ENABLE_API=True
ENABLE_MONITORING=True
ENABLE_CACHE=True