# 🚀 Affiliate Strategist Pro (Django)

Plataforma de análisis y generación de estrategias de marketing con IA.

Diseñada para desplegarse rápidamente en Railway (PaaS), con soporte para PostgreSQL o SQLite y archivos estáticos servidos con WhiteNoise.

---

## ✅ Estado y versiones
- Python: 3.11.x
- Django: 5.2.x
- Servidor: Gunicorn + WhiteNoise
- IA: Google Generative AI (Gemini)

---

## 📁 Estructura del repositorio
```
.
├── manage.py                  # Entry point de Django
├── config/                    # Proyecto Django (urls, settings, wsgi)
│   ├── settings.py            # Config principal (usa SQLite si no hay PG)
│   ├── urls.py
│   └── wsgi.py
├── analyzer/                  # App principal
│   ├── models.py
│   ├── views.py               # Home + endpoints (análisis, historial, pdf)
│   ├── views_auth.py          # Login, registro, perfil, upgrade
│   ├── urls.py
│   └── templates/
├── requirements.txt           # Dependencias
├── Procfile                   # Comando de inicio (migraciones + collectstatic + gunicorn)
├── runtime.txt                # Versión de Python
└── README.md
```

---

## 🧪 Desarrollo local (rápido)
1) Requisitos: Python 3.11

2) Instalar dependencias:
```bash
pip install -r requirements.txt
```

3) Migraciones y servidor local:
```bash
python manage.py migrate
python manage.py runserver
```

4) Acceso: `http://127.0.0.1:8000`

Opcional: crear superusuario
```bash
python manage.py createsuperuser
```

---

## 🔑 Variables de entorno
- SECRET_KEY: clave secreta de Django (obligatoria en producción)
- DEBUG: "True"/"False" (en Railway se recomienda False)
- ALLOWED_HOSTS: dominios permitidos (opcional; en `DEBUG=True` se relaja)

Base de datos (opcional, si no se definen se usa SQLite automáticamente):
- PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE (Railway Postgres)
- o `DATABASE_URL`/`DB_HOST`/`DB_*` equivalentes

IA (opcional):
- Puedes ingresar tu API key de Gemini en la UI al realizar un análisis.

---

## 🚀 Deploy en Railway (recomendado)
Este repositorio ya está preparado para Railway.

### Pasos
1) En Railway, crea un proyecto y selecciona “Deploy from GitHub Repo”.
2) Conecta este repositorio y la rama que quieras desplegar.
3) Variables (Settings → Variables):
   - `SECRET_KEY`: genera una clave segura
   - `DEBUG`: `False` (recomendado) o `True` para pruebas
   - Si quieres Postgres: añade un servicio de PostgreSQL y Railway expondrá `PG*`. Si NO añades Postgres, la app usará SQLite automáticamente (no necesitas setear nada).
4) Deploy. El `Procfile` ejecuta:
   - Migraciones
   - `collectstatic` (WhiteNoise sirve estáticos)
   - Gunicorn (`config.wsgi:application`)
5) Abre el dominio de Railway.

### Notas importantes
- Archivos estáticos: WhiteNoise está habilitado en `config/settings.py`.
- Base de datos:
  - Si existen variables `PG*`/`DATABASE_URL`, se usa PostgreSQL.
  - Si NO existen, se usa SQLite (simple para entornos sin DB administrada).
- Procfile ya corre `collectstatic` con `--noinput` y lanza Gunicorn.

### Solución de problemas en Railway
- “connection refused 127.0.0.1:5432”: o bien conecta un servicio de Postgres (y Railway inyectará `PG*`), o elimina cualquier variable `PG*` para usar SQLite.
- “Pillow no instalado / ImageField”: ya está incluido `Pillow` en `requirements.txt`.
- “STATICFILES_DIRS no existe”: ya está configurado para ser condicional; el warning no aparecerá si no hay carpeta `static/`.

---

## 🌐 Deploy en otras plataformas

### Heroku
- Requisitos: tener `Procfile` (ya existe), `runtime.txt` (ya existe).
- Variables: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, y opcionales `PG*` si usas Heroku Postgres.
- Comando de inicio (Procfile):
  ```
  web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
  ```
- WhiteNoise ya sirve los archivos estáticos.

### Docker / VPS (Gunicorn + Nginx)
- Usa la imagen `python:3.11-slim`.
- Instala dependencias con `pip install -r requirements.txt`.
- Variables: define `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, y configura Postgres o permite el fallback a SQLite.
- Comando de inicio:
  ```bash
  gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
  ```
- Nginx como reverse proxy (opcional) sirviendo `/static/` desde `staticfiles/`.

### Render, Fly.io, etc.
- Start command: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
- Asegura variables (`SECRET_KEY`, `DEBUG`, base de datos) y que se ejecute `python manage.py migrate` y `python manage.py collectstatic --noinput` durante el build/deploy.

---

## 🧠 Funcionalidades clave
- Análisis básico y competitivo con IA (Google Gemini)
- Autenticación: login, registro, perfil, planes
- Historial personal y público
- Exportación a PDF (ReportLab)
- WhiteNoise para estáticos en producción

Rutas principales:
- `/` (GET/POST): home y creación de análisis
- `/login/`, `/register/`, `/logout/`, `/profile/`, `/upgrade/`
- `/history/`, `/public-history/`
- `/download-pdf/<uuid>/`

---

## 🔍 Troubleshooting común
- No puedo descargar PDF: revisa que el análisis exista y usa el enlace directo `/download-pdf/<id>/`.
- Error de DB en producción: elimina variables `PG*` para usar SQLite o conecta el servicio Postgres.
- Error de estáticos/CSS: verifica que `collectstatic` corra en el deploy (en Railway lo hace el `Procfile`).

---

## 📄 Licencia
MIT. Ver `LICENSE` si aplica.

## 👤 Autor
- Raul Pivet (@Sinsapiar1)

---

Si este proyecto te resulta útil, ¡deja una estrella! ⭐