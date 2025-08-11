# analyzer/urls.py - CONFIGURACIÓN CORREGIDA PARA PDF

from django.urls import path
from .views import (
    AffiliateStrategistView,
    UserHistoryView,
    PublicHistoryView,
    download_pdf,
    test_pdf  # Para debugging
)

# ✅ IMPORTAR VISTAS DE AUTH SI EXISTEN
try:
    from .views_auth import (
        RegisterView,
        LoginView,
        LogoutView,
        ProfileView,
        UpgradeView
    )
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

app_name = 'analyzer'

urlpatterns = [
    # ✅ PÁGINA PRINCIPAL
    path('', AffiliateStrategistView.as_view(), name='home'),
    
    # ✅ DESCARGA DE PDF - IMPORTANTE: UUID COMPATIBLE
    path('download-pdf/<uuid:analysis_id>/', download_pdf, name='download_pdf'),
    path('download-pdf/<str:analysis_id>/', download_pdf, name='download_pdf_str'),  # Fallback
    
    # ✅ VISTA DE PRUEBA PARA PDF
    path('test-pdf/', test_pdf, name='test_pdf'),
    
    # ✅ HISTORIAL
    path('history/', UserHistoryView.as_view(), name='user_history'),
    path('public-history/', PublicHistoryView.as_view(), name='public_history'),
]

# ✅ AGREGAR RUTAS DE AUTH SI ESTÁN DISPONIBLES
if AUTH_AVAILABLE:
    auth_patterns = [
        path('register/', RegisterView.as_view(), name='register'),
        path('login/', LoginView.as_view(), name='login'),
        path('logout/', LogoutView.as_view(), name='logout'),
        path('profile/', ProfileView.as_view(), name='profile'),
        path('upgrade/', UpgradeView.as_view(), name='upgrade'),
    ]
    urlpatterns.extend(auth_patterns)

# =============================================================================
# TAMBIÉN ACTUALIZAR config/urls.py SI ES NECESARIO

"""
# config/urls.py - ASEGURAR CONFIGURACIÓN CORRECTA

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('analyzer.urls')),  # ✅ IMPORTANTE: Sin namespace aquí
]

# ✅ SERVIR ARCHIVOS MEDIA EN DESARROLLO
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
"""