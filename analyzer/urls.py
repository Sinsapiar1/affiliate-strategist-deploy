from django.urls import path
from . import views
from .views_auth import LoginView, RegisterView, LogoutView, ProfileView, UpgradeView
from .monetization import upgrade_page, process_upgrade, monetization_popup_data

app_name = 'analyzer'

urlpatterns = [
    path('', views.home, name='home'),
    # Autenticación
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('upgrade/', upgrade_page, name='upgrade'),
    path('process-upgrade/', process_upgrade, name='process_upgrade'),
    path('api/monetization-popup/', monetization_popup_data, name='monetization_popup'),
    # Historial
    path('history/', views.history, name='history'),
    path('public-history/', views.public_history, name='public_history'),
    # PDF
    path('download-pdf/<uuid:analysis_id>/', views.download_pdf, name='download_pdf'),
]
