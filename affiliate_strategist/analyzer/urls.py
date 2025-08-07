# analyzer/urls.py
# URLs actualizadas con sistema de usuarios

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

urlpatterns = [
    # Página principal
    path('', AffiliateStrategistView.as_view(), name='home'),
    
    # Autenticación
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Perfil y cuenta
    path('profile/', ProfileView.as_view(), name='profile'),
    path('upgrade/', UpgradeView.as_view(), name='upgrade'),
    
    # Historial
    path('history/', UserHistoryView.as_view(), name='user_history'),
    path('public-history/', PublicHistoryView.as_view(), name='public_history'),
    
    # Descargas
    path('download-pdf/<int:analysis_id>/', download_pdf, name='download_pdf'),
]