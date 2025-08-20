from django.urls import path
from . import views
from .views_auth import LoginView, RegisterView, LogoutView, ProfileView, UpgradeView

app_name = 'analyzer'

urlpatterns = [
    path('', views.home, name='home'),
    # Autenticación
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('upgrade/', UpgradeView.as_view(), name='upgrade'),
    # Historial
    path('history/', views.history, name='history'),
    path('public-history/', views.public_history, name='public_history'),
    # PDF
    path('download-pdf/<uuid:analysis_id>/', views.download_pdf, name='download_pdf'),
]
