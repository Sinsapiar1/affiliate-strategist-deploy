# README.md - DOCUMENTACIÓN PRINCIPAL

# 🚀 Affiliate Strategist Pro v1.3

> **Generador de estrategias de marketing de afiliados con IA avanzada**

[![Django](https://img.shields.io/badge/Django-5.2.4-green.svg)](https://djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/Coverage-95%25-brightgreen.svg)](coverage/)

**Affiliate Strategist Pro** es una aplicación web avanzada que utiliza inteligencia artificial para generar estrategias de marketing de afiliados personalizadas, análisis competitivos y contenido optimizado para diferentes plataformas sociales.

## ✨ **Características Principales**

### 🤖 **IA Avanzada**
- **Integración con Google Gemini Pro** para análisis inteligentes
- **Análisis competitivo automático** con comparación de precios
- **Generación de contenido personalizado** por plataforma
- **Optimización de hashtags y keywords** automática

### 📊 **Analytics y Métricas**
- **Dashboard de métricas en tiempo real** para administradores
- **Historial completo de análisis** con búsqueda avanzada
- **Estadísticas de rendimiento** por usuario y plataforma
- **Sistema de cache inteligente** para optimización

### 👥 **Sistema de Usuarios**
- **Autenticación completa** con registro/login
- **Planes de suscripción** (Gratuito, Pro, Premium)
- **Sistema de gamificación** con puntos y niveles
- **Perfiles personalizados** con estadísticas

### 🔌 **API REST Completa**
- **Endpoints documentados** para integración
- **Autenticación por token** para seguridad
- **Rate limiting** y throttling
- **Paginación automática** de resultados

### 🛡️ **Seguridad y Rendimiento**
- **Middleware de seguridad** personalizado
- **Sistema de cache Redis** para alta performance
- **Rate limiting** contra abuso
- **Logging y monitoreo** completo

## 🚀 **Inicio Rápido**

### Prerequisitos
- Python 3.11+
- Node.js 18+ (opcional, para desarrollo frontend)
- Redis (recomendado para cache)
- PostgreSQL (recomendado para producción)

### Instalación Local

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/affiliate-strategist-pro.git
cd affiliate-strategist-pro

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# 5. Ejecutar migraciones
python manage.py migrate

# 6. Crear superusuario
python manage.py createsuperuser

# 7. Iniciar servidor
python manage.py runserver
```

🎉 **¡Listo!** Visita `http://localhost:8000` para usar la aplicación.

### Instalación con Docker

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/affiliate-strategist-pro.git
cd affiliate-strategist-pro

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# 3. Construir y ejecutar
docker-compose up -d

# 4. Ejecutar migraciones
docker-compose exec web python manage.py migrate

# 5. Crear superusuario
docker-compose exec web python manage.py createsuperuser
```

## 🛠️ **Configuración**

### Variables de Entorno Principales

```env
# Django
SECRET_KEY=tu-secret-key-super-segura
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos
DATABASE_URL=postgresql://user:pass@localhost/affiliate_strategist

# APIs
GEMINI_API_KEY=tu-api-key-de-gemini
OPENAI_API_KEY=tu-api-key-de-openai

# Cache
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-password
```

### Obtener API Keys

1. **Google Gemini**: Visita [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **OpenAI** (opcional): Visita [OpenAI Platform](https://platform.openai.com/api-keys)

## 📖 **Documentación**

### Para Usuarios
- [🔰 Guía de Usuario](docs/user-guide.md) - Cómo usar la aplicación
- [💡 Casos de Uso](docs/use-cases.md) - Ejemplos prácticos
- [❓ FAQ](docs/faq.md) - Preguntas frecuentes

### Para Desarrolladores
- [🚀 Guía de Desarrollo](docs/development.md) - Setup desarrollo
- [🔌 Documentación API](docs/api.md) - Endpoints y ejemplos
- [🏗️ Arquitectura](docs/architecture.md) - Diseño del sistema
- [🧪 Testing](docs/testing.md) - Ejecutar tests
- [🚀 Deployment](docs/deployment.md) - Deploy a producción

### Para Contribuidores
- [🤝 Guía de Contribución](CONTRIBUTING.md) - Cómo contribuir
- [📋 Código de Conducta](CODE_OF_CONDUCT.md) - Normas de comportamiento
- [🗺️ Roadmap](docs/roadmap.md) - Funcionalidades futuras

## 🎯 **Casos de Uso**

### 🎬 **YouTuber de Tech Reviews**
```bash
✅ Analiza producto tecnológico
✅ Genera estrategia para YouTube
✅ Optimiza para audiencia tech-savvy
✅ Sugiere momento ideal para publicar
✅ Genera hashtags específicos
```

### 📱 **Influencer de Instagram**
```bash
✅ Análisis competitivo automático
✅ Estrategia visual para Instagram
✅ Hooks para captar atención
✅ Stories y posts coordinados
✅ Métricas de engagement
```

### 💼 **Marketer Profesional**
```bash
✅ Análisis multi-plataforma
✅ ROI y métricas avanzadas
✅ Segmentación de audiencia
✅ A/B testing de mensajes
✅ Reports ejecutivos en PDF
```

## 🔧 **Comandos Útiles**

### Desarrollo
```bash
# Ejecutar tests
python manage.py test

# Generar datos de prueba
python manage.py generate_test_data --users 10 --analyses 50

# Limpiar análisis antiguos
python manage.py cleanup_old_analyses --days 30

# Actualizar plantillas
python manage.py update_templates

# Cachear datos frecuentes
python manage.py manage_cache warm
```

### Producción
```bash
# Deploy completo
./deployment/scripts/deploy.sh

# Backup de base de datos
./deployment/scripts/deploy.sh backup

# Ver logs en tiempo real
./deployment/scripts/deploy.sh logs

# Verificar salud del sistema
./deployment/scripts/deploy.sh health
```

## 📊 **Métricas y Monitoreo**

### Dashboard de Admin
- Accede a `/admin/metrics/` para ver métricas en tiempo real
- Monitoreo de CPU, memoria y disco
- Estadísticas de usuarios y análisis
- Alertas automáticas de sistema

### API de Métricas
```bash
# Estadísticas generales
GET /api/analyses/stats/

# Métricas de usuario
GET /api/profile/

# Notificaciones
GET /api/notifications/
```

## 🚨 **Troubleshooting**

### Problemas Comunes

**Error 500 en análisis:**
```bash
# Verificar API key de Gemini
echo $GEMINI_API_KEY

# Verificar logs
tail -f logs/django.log

# Reiniciar cache
python manage.py manage_cache clear
```

**Problemas de performance:**
```bash
# Verificar cache Redis
redis-cli ping

# Optimizar base de datos
python manage.py dbshell
ANALYZE;

# Verificar uso de memoria
python manage.py shell
>>> import psutil; psutil.virtual_memory()
```

**Errores de scraping:**
```bash
# Verificar conectividad
curl -I https://example.com/producto

# Actualizar User-Agent
python manage.py shell
>>> from analyzer.utils.scraping import update_user_agent
>>> update_user_agent()
```

## 🤝 **Contribución**

¡Las contribuciones son bienvenidas! Por favor:

1. **Fork** el repositorio
2. **Crea** una rama feature (`git checkout -b feature/amazing-feature`)
3. **Commit** tus cambios (`git commit -m 'Add amazing feature'`)
4. **Push** a la rama (`git push origin feature/amazing-feature`)
5. **Abre** un Pull Request

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para más detalles.

## 📄 **Licencia**

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

## 🙏 **Agradecimientos**

- [Django](https://djangoproject.com/) - Framework web
- [Google Gemini](https://ai.google.dev/) - IA para análisis
- [Bootstrap](https://getbootstrap.com/) - UI Framework
- [Redis](https://redis.io/) - Sistema de cache
- [PostgreSQL](https://postgresql.org/) - Base de datos

## 📞 **Soporte**

- 📧 **Email**: soporte@affiliatestrategist.com
- 💬 **Discord**: [Unirse al servidor](https://discord.gg/affiliate-strategist)
- 📖 **Documentación**: [docs.affiliatestrategist.com](https://docs.affiliatestrategist.com)
- 🐛 **Issues**: [GitHub Issues](https://github.com/tu-usuario/affiliate-strategist-pro/issues)

---

<div align="center">

**Hecho con ❤️ por [Tu Nombre](https://github.com/tu-usuario)**

[⭐ Danos una estrella](https://github.com/tu-usuario/affiliate-strategist-pro) si te gustó el proyecto!

</div>

# =============================================================================
# docs/api.md - DOCUMENTACIÓN DE API

# 🔌 API Documentation - Affiliate Strategist Pro

## Introducción

La API REST de Affiliate Strategist Pro permite integrar la funcionalidad de generación de estrategias de marketing en aplicaciones externas.

### Base URL
```
https://tu-dominio.com/api/
```

### Autenticación

La API utiliza **Token Authentication**. Primero obtén un token:

```bash
POST /api/auth/token/
Content-Type: application/json

{
    "username": "tu_usuario",
    "password": "tu_password"
}
```

**Respuesta:**
```json
{
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

**Uso del token:**
```bash
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

## Endpoints Principales

### 📊 Análisis

#### Crear Análisis
```http
POST /api/analyze/
Authorization: Token <tu-token>
Content-Type: application/json

{
    "product_url": "https://example.com/producto",
    "platform": "tiktok",
    "target_audience": "mujeres 25-35 años",
    "campaign_goal": "conversions",
    "budget": "medium",
    "tone": "professional",
    "analysis_type": "basic",
    "api_key": "tu-gemini-api-key"
}
```

**Respuesta exitosa (201):**
```json
{
    "success": true,
    "analysis_id": "123e4567-e89b-12d3-a456-426614174000",
    "response": "## Estrategia de Marketing...",
    "product": {
        "title": "Producto Ejemplo",
        "price": "$99.99",
        "description": "Descripción del producto..."
    },
    "message": "¡Análisis completado exitosamente!"
}
```

#### Obtener Análisis
```http
GET /api/analyses/
Authorization: Token <tu-token>
```

**Parámetros de consulta:**
- `page`: Número de página (default: 1)
- `page_size`: Elementos por página (max: 100)
- `platform`: Filtrar por plataforma
- `analysis_type`: Filtrar por tipo de análisis
- `search`: Buscar en título o descripción

**Respuesta:**
```json
{
    "count": 25,
    "next": "https://api.example.com/analyses/?page=2",
    "previous": null,
    "results": [
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "product_title": "Producto Ejemplo",
            "platform": "tiktok",
            "analysis_type": "basic",
            "success": true,
            "created_at": "2024-01-15T10:30:00Z",
            "is_recent": true
        }
    ]
}
```

#### Obtener Análisis Específico
```http
GET /api/analyses/{id}/
Authorization: Token <tu-token>
```

### 👤 Usuario y Perfil

#### Obtener Perfil
```http
GET /api/profile/
Authorization: Token <tu-token>
```

**Respuesta:**
```json
{
    "bio": "Experto en marketing digital",
    "website": "https://miwebsite.com",
    "company_name": "Mi Empresa",
    "plan": "pro",
    "plan_display": "⭐ Profesional",
    "analyses_remaining": 85,
    "success_rate": 92.5,
    "total_analyses": 120,
    "points": 2400,
    "level": 3
}
```

#### Actualizar Perfil
```http
PATCH /api/profile/
Authorization: Token <tu-token>
Content-Type: application/json

{
    "bio": "Nueva biografía",
    "website": "https://nuevo-sitio.com",
    "preferred_platforms": ["tiktok", "instagram"]
}
```

### 📝 Plantillas de Marketing

#### Obtener Plantillas
```http
GET /api/templates/
Authorization: Token <tu-token>
```

**Parámetros:**
- `platform`: Filtrar por plataforma
- `category`: Filtrar por categoría
- `ordering`: Ordenar por (`success_rate`, `times_used`, `created_at`)

**Respuesta:**
```json
{
    "results": [
        {
            "id": "template-uuid",
            "name": "Review Tech YouTube",
            "platform": "youtube",
            "category": "technology",
            "template": "Hey! Hoy te traigo un review HONESTO de [PRODUCTO]...",
            "success_rate": 85.5,
            "times_used": 245,
            "is_premium": false
        }
    ]
}
```

#### Usar Plantilla
```http
POST /api/templates/{id}/use_template/
Authorization: Token <tu-token>
```

### 📊 Estadísticas

#### Estadísticas Generales
```http
GET /api/analyses/stats/
Authorization: Token <tu-token>
```

**Respuesta:**
```json
{
    "summary": {
        "total": 1250,
        "successful": 1156,
        "success_rate": 92.5
    },
    "by_platform": [
        {"platform": "tiktok", "count": 450},
        {"platform": "instagram", "count": 380}
    ],
    "by_type": [
        {"analysis_type": "basic", "count": 800},
        {"analysis_type": "competitive", "count": 450}
    ],
    "daily_trend": [
        {"date": "2024-01-15", "count": 25},
        {"date": "2024-01-16", "count": 30}
    ]
}
```

### 🔔 Notificaciones

#### Obtener Notificaciones
```http
GET /api/notifications/
Authorization: Token <tu-token>
```

#### Marcar como Leída
```http
PATCH /api/notifications/{id}/mark_as_read/
Authorization: Token <tu-token>
```

#### Marcar Todas como Leídas
```http
PATCH /api/notifications/mark_all_read/
Authorization: Token <tu-token>
```

## Rate Limiting

La API implementa rate limiting para prevenir abuso:

- **Análisis**: 10 por hora por usuario autenticado
- **API General**: 100 requests por hora por usuario
- **Usuarios anónimos**: 20 requests por hora por IP

**Headers de respuesta:**
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1642248000
```

## Códigos de Error

### Errores Comunes

**400 Bad Request**
```json
{
    "error": "Datos de entrada inválidos",
    "details": {
        "product_url": ["Este campo es requerido"],
        "platform": ["Selecciona una opción válida"]
    }
}
```

**401 Unauthorized**
```json
{
    "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden**
```json
{
    "error": "Has alcanzado el límite de análisis para tu plan"
}
```

**404 Not Found**
```json
{
    "detail": "Not found."
}
```

**429 Too Many Requests**
```json
{
    "error": "Rate limit exceeded. Try again in 3600 seconds."
}
```

**500 Internal Server Error**
```json
{
    "error": "Error interno del servidor"
}
```

## Ejemplos de Uso

### Python con requests
```python
import requests

# Obtener token
response = requests.post('https://api.example.com/auth/token/', {
    'username': 'tu_usuario',
    'password': 'tu_password'
})
token = response.json()['token']

# Headers para requests
headers = {
    'Authorization': f'Token {token}',
    'Content-Type': 'application/json'
}

# Crear análisis
analysis_data = {
    'product_url': 'https://example.com/producto',
    'platform': 'tiktok',
    'target_audience': 'jóvenes 18-25',
    'analysis_type': 'basic',
    'api_key': 'tu-gemini-key'
}

response = requests.post(
    'https://api.example.com/analyze/',
    json=analysis_data,
    headers=headers
)

if response.status_code == 201:
    result = response.json()
    print(f"Análisis creado: {result['analysis_id']}")
    print(f"Estrategia: {result['response']}")
```

### JavaScript con fetch
```javascript
// Obtener token
const tokenResponse = await fetch('https://api.example.com/auth/token/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        username: 'tu_usuario',
        password: 'tu_password'
    })
});

const { token } = await tokenResponse.json();

// Crear análisis
const analysisResponse = await fetch('https://api.example.com/analyze/', {
    method: 'POST',
    headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        product_url: 'https://example.com/producto',
        platform: 'tiktok',
        target_audience: 'millennials',
        analysis_type: 'basic',
        api_key: 'tu-gemini-key'
    })
});

const result = await analysisResponse.json();
console.log('Estrategia generada:', result.response);
```

### cURL
```bash
# Obtener token
curl -X POST https://api.example.com/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"tu_usuario","password":"tu_password"}'

# Crear análisis
curl -X POST https://api.example.com/analyze/ \
  -H "Authorization: Token tu-token-aqui" \
  -H "Content-Type: application/json" \
  -d '{
    "product_url": "https://example.com/producto",
    "platform": "tiktok",
    "target_audience": "millennials",
    "analysis_type": "basic",
    "api_key": "tu-gemini-key"
  }'
```

## Webhooks (Próximamente)

Los webhooks permitirán recibir notificaciones en tiempo real cuando se completen análisis o ocurran eventos importantes.

```json
{
    "event": "analysis.completed",
    "data": {
        "analysis_id": "123e4567-e89b-12d3-a456-426614174000",
        "user_id": "user-123",
        "success": true,
        "completed_at": "2024-01-15T10:30:00Z"
    }
}
```

## SDKs Oficiales

### Python SDK (En desarrollo)
```bash
pip install affiliate-strategist-sdk
```

```python
from affiliate_strategist import Client

client = Client(api_key='tu-token')
analysis = client.analyze(
    product_url='https://example.com/producto',
    platform='tiktok'
)
print(analysis.strategy)
```

### JavaScript SDK (En desarrollo)
```bash
npm install affiliate-strategist-js
```

```javascript
import { AffiliateStrategist } from 'affiliate-strategist-js';

const client = new AffiliateStrategist('tu-token');
const analysis = await client.analyze({
    productUrl: 'https://example.com/producto',
    platform: 'tiktok'
});
```

## Soporte

- 📧 **API Support**: api-support@affiliatestrategist.com
- 📖 **Documentación**: [docs.affiliatestrategist.com/api](https://docs.affiliatestrategist.com/api)
- 💬 **Discord**: [#api-support](https://discord.gg/affiliate-strategist)

---

**Última actualización**: Enero 2024  
**Versión API**: v1.3