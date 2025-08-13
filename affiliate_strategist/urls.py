# config/urls.py - CONFIGURACIÓN CORREGIDA

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ✅ RUTA PRINCIPAL - Debe apuntar al analyzer
    path('', include('analyzer.urls')),
    
    # ✅ Rutas adicionales si las necesitas
    # path('api/', include('analyzer.api_urls')),  # Para APIs futuras
]

# ✅ SERVIR archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)