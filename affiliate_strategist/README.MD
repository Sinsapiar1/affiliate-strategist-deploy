# 🚀 Affiliate Strategist - AI-Powered Marketing Platform

<div align="center">

![Django](https://img.shields.io/badge/Django-5.0+-green.svg)
![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Gemini AI](https://img.shields.io/badge/AI-Google_Gemini-orange.svg)
![Status](https://img.shields.io/badge/Status-Production_Ready-success.svg)

**Plataforma inteligente de análisis y estrategias de marketing para afiliados con IA**

[Ver Demo](#demo) | [Documentación](./DEVELOPMENT_GUIDE.md) | [Reportar Bug](https://github.com/Sinsapiar1/Afiliate_strategist/issues)

</div>

---

## 📁 Estructura del Proyecto

```
Afiliate_strategist/                  # ← Repositorio GitHub (estás aquí)
│
├── 📄 README.md                       # ← Este archivo
├── 📄 DEVELOPMENT_GUIDE.md           # Guía completa de desarrollo
├── 📄 API_DOCUMENTATION.md           # Documentación de API
├── 📄 LICENSE                         # Licencia del proyecto
│
└── 📁 affiliate_strategist/           # ← Proyecto Django
    ├── 📁 analyzer/                   # App principal
    │   ├── models.py                  # Modelos de datos
    │   ├── views.py                   # Vistas y lógica
    │   ├── urls.py                    # Rutas de la app
    │   ├── forms.py                   # Formularios
    │   ├── ai_handler.py              # Integración con Gemini
    │   └── templates/                 # Templates HTML
    │       ├── base.html
    │       ├── index.html
    │       ├── results.html
    │       └── history.html
    │
    ├── 📁 affiliate_strategist/       # Configuración Django
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    │
    ├── 📁 static/                     # Archivos estáticos
    │   ├── css/
    │   ├── js/
    │   └── img/
    │
    ├── 📁 media/                      # Archivos subidos
    │   └── avatars/
    │
    ├── 📁 venv/                       # Entorno virtual (no subir)
    │
    ├── 📄 manage.py                   # Script principal Django
    ├── 📄 requirements.txt            # Dependencias Python
    ├── 📄 db.sqlite3                  # Base de datos (desarrollo)
    └── 📄 .env                        # Variables de entorno (no subir)
```

## ✨ Características Principales

### 🎯 Funcionalidades Core

- **🤖 Análisis con IA** - Google Gemini Pro para estrategias inteligentes
- **📊 Multi-plataforma** - TikTok, Instagram, YouTube, Facebook, Twitter, LinkedIn, Pinterest
- **👥 Sistema de Usuarios** - Autenticación completa con planes Free/Pro/Premium
- **📈 Dashboard Analytics** - Métricas y estadísticas en tiempo real
- **🎨 Plantillas de Marketing** - Biblioteca de templates optimizados
- **🏆 Gamificación** - Sistema de puntos, niveles y logros
- **🔔 Notificaciones** - Alertas y actualizaciones automáticas
- **📄 Exportación PDF** - Descarga de análisis en formato profesional

### 🔧 Características Técnicas

- **Django 5.0+** - Framework web robusto
- **PostgreSQL/SQLite** - Base de datos flexible
- **Bootstrap 5** - UI moderna y responsive
- **Cache System** - Optimización de rendimiento
- **API REST** - Endpoints para integraciones
- **Rate Limiting** - Control de uso por usuario

## 🚀 Instalación Rápida

### Prerequisitos
- Python 3.11 o superior
- pip y venv
- Git
- API Key de Google Gemini (opcional)

### Pasos de Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/Sinsapiar1/Afiliate_strategist.git
cd Afiliate_strategist

# 2. Entrar a la carpeta del proyecto Django
cd affiliate_strategist

# 3. Crear entorno virtual
python -m venv venv

# 4. Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 5. Instalar dependencias
pip install -r requirements.txt

# 6. Configurar base de datos
python manage.py makemigrations
python manage.py migrate

# 7. Crear superusuario (opcional)
python manage.py createsuperuser

# 8. Ejecutar servidor
python manage.py runserver
```

✅ **¡Listo!** Abre tu navegador en `http://127.0.0.1:8000`

## 🔑 Configuración

### Variables de Entorno (.env)

Crea un archivo `.env` en la carpeta `affiliate_strategist/`:

```env
# Django
SECRET_KEY=tu-clave-secreta-super-segura
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos (opcional, por defecto usa SQLite)
DATABASE_URL=postgresql://user:pass@localhost/dbname

# API Keys (opcional, usuarios pueden usar la suya)
GEMINI_API_KEY=AIza...

# Email (opcional)
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-password
```

### Obtener API Key de Gemini

1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crea una cuenta o inicia sesión
3. Genera una nueva API Key
4. Los usuarios pueden ingresar su propia key en la interfaz

## 📖 Uso Básico

### 1. Análisis de Producto

1. Ingresa la URL del producto
2. Selecciona la plataforma (TikTok, Instagram, etc.)
3. Define tu audiencia objetivo
4. Ingresa tu API Key de Gemini
5. ¡Obtén tu estrategia personalizada!

### 2. Historial y Gestión

- Ve a `/history` para ver todos tus análisis
- Descarga cualquier análisis como PDF
- Comparte análisis con enlaces únicos
- Marca favoritos para acceso rápido

### 3. Panel de Usuario

- Revisa tu plan y límites en `/profile`
- Monitorea tus estadísticas
- Gestiona notificaciones
- Sigue tu progreso con puntos y niveles

## 🏗️ Modelos de Datos

### Modelos Principales

- **AnalysisHistory** - Historial completo de análisis
- **UserProfile** - Perfiles extendidos de usuario
- **MarketingTemplate** - Plantillas de marketing
- **Notification** - Sistema de notificaciones
- **AnalysisFeedback** - Feedback y ratings
- **DailyMetrics** - Métricas del sistema

Ver [models.py](./affiliate_strategist/analyzer/models.py) para detalles completos.

## 📊 Planes y Límites

| Plan | Análisis/Mes | Características | Precio |
|------|--------------|-----------------|--------|
| 🆓 **Free** | 5 | Análisis básicos, PDF | Gratis |
| ⭐ **Pro** | 100 | + Análisis competitivos, Plantillas premium | $9.99 |
| 💎 **Premium** | Ilimitado | + API Access, Soporte 24/7 | $29.99 |
| 🏢 **Enterprise** | Ilimitado | + Personalización, SLA | Contactar |

## 🛠️ Desarrollo

### Estructura de la App Principal

```python
# analyzer/views.py - Vista principal
class IndexView(View):
    def post(self, request):
        # Procesa formulario
        # Llama a Gemini AI
        # Guarda en base de datos
        # Retorna resultado
```

### Agregar Nueva Funcionalidad

1. Actualiza modelos si es necesario
2. Crea/modifica vistas
3. Actualiza templates
4. Ejecuta migraciones
5. Añade tests

Ver [DEVELOPMENT_GUIDE.md](./DEVELOPMENT_GUIDE.md) para guía completa.

## 🧪 Testing

```bash
# Ejecutar todos los tests
python manage.py test

# Test específico
python manage.py test analyzer.tests.TestAnalysis

# Con coverage
coverage run --source='.' manage.py test
coverage report
```

## 🚀 Deployment

### Opción 1: Heroku

```bash
# Instalar Heroku CLI
# Crear Procfile
echo "web: gunicorn affiliate_strategist.wsgi" > Procfile

# Deploy
heroku create tu-app-name
git push heroku main
heroku run python manage.py migrate
```

### Opción 2: VPS con Gunicorn + Nginx

Ver [DEPLOYMENT.md](./DEPLOYMENT.md) para guía completa.

## 📝 Roadmap

### ✅ Completado
- [x] Análisis básico con IA
- [x] Sistema de usuarios
- [x] Historial de análisis
- [x] Exportación PDF
- [x] Sistema de plantillas

### 🔄 En Progreso
- [ ] Dashboard analytics mejorado
- [ ] API REST completa
- [ ] Sistema de cache Redis

### 📅 Próximamente
- [ ] Análisis en lote (CSV)
- [ ] Integración con más plataformas
- [ ] App móvil
- [ ] Webhooks
- [ ] Multi-idioma completo

## 🤝 Contribuir

¡Las contribuciones son bienvenidas!

1. Fork el proyecto
2. Crea tu feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add: nueva funcionalidad'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 🐛 Reportar Bugs

Si encuentras un bug, por favor:

1. Abre un [Issue](https://github.com/Sinsapiar1/Afiliate_strategist/issues)
2. Incluye:
   - Descripción del problema
   - Pasos para reproducir
   - Comportamiento esperado
   - Screenshots si aplica
   - Tu entorno (OS, Python version, etc.)

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver [LICENSE](./LICENSE) para detalles.

## 👨‍💻 Autor

**Raul Pivet** - [@Sinsapiar1](https://github.com/Sinsapiar1)

## 🙏 Agradecimientos

- [Django](https://djangoproject.com/) - Framework web
- [Google Gemini](https://ai.google.dev/) - IA para análisis
- [Bootstrap](https://getbootstrap.com/) - Framework CSS
- [Font Awesome](https://fontawesome.com/) - Iconos

## 📞 Soporte

- 📧 Email: [tu-email@example.com]
- 🐛 Issues: [GitHub Issues](https://github.com/Sinsapiar1/Afiliate_strategist/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/Sinsapiar1/Afiliate_strategist/discussions)

---

<div align="center">

**⭐ Si te gusta este proyecto, dale una estrella!**

[⬆ Volver arriba](#-affiliate-strategist---ai-powered-marketing-platform)

</div>