# analyzer/urls.py - CONFIGURACIÓN MEJORADA

from django.urls import path
from .views import (
    AffiliateStrategistView,
    UserHistoryView,
    PublicHistoryView,
    download_pdf
)
from .views_auth import (
    RegisterView,
    LoginView,
    LogoutView,
    ProfileView,
    UpgradeView
)

# ✅ NAMESPACE para evitar conflictos
app_name = 'analyzer'

urlpatterns = [
    # ✅ PÁGINA PRINCIPAL - Acepta GET y POST
    path('', AffiliateStrategistView.as_view(), name='home'),
    
    # ✅ AUTENTICACIÓN
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # ✅ PERFIL Y CUENTA
    path('profile/', ProfileView.as_view(), name='profile'),
    path('upgrade/', UpgradeView.as_view(), name='upgrade'),
    
    # ✅ HISTORIAL
    path('history/', UserHistoryView.as_view(), name='user_history'),
    path('public-history/', PublicHistoryView.as_view(), name='public_history'),
    
    # ✅ DESCARGAS
    path('download-pdf/<int:analysis_id>/', download_pdf, name='download_pdf'),
    
    # ✅ RUTAS API FUTURAS (preparadas)
    # path('api/analyze/', AnalyzeAPIView.as_view(), name='api_analyze'),
    # path('api/templates/', TemplatesAPIView.as_view(), name='api_templates'),
]