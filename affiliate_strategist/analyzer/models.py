# analyzer/models.py
# VERSIÓN ARREGLADA - UNA SOLA DEFINICIÓN DE CADA MODELO

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime, timedelta
import uuid

# ============= MODELO PRINCIPAL DE ANÁLISIS =============
class AnalysisHistory(models.Model):
    """Modelo principal para guardar análisis"""
    
    # Datos básicos del análisis
    product_url = models.URLField(max_length=500)
    target_audience = models.TextField()
    platform = models.CharField(max_length=50, choices=[
        ('instagram', 'Instagram'),
        ('tiktok', 'TikTok'),
        ('facebook', 'Facebook'),
        ('youtube', 'YouTube'),
        ('blog', 'Blog'),
        ('email', 'Email Marketing'),
        ('twitter', 'Twitter/X'),
    ])
    
    # Datos del producto
    product_url = models.URLField()
    product_title = models.CharField(max_length=255)
    product_price = models.CharField(max_length=100, blank=True, null=True)
    product_description = models.TextField(blank=True, null=True)
    platform = models.CharField(max_length=50)
    target_audience = models.CharField(max_length=200)
    additional_context = models.TextField(blank=True, null=True)
    campaign_goal = models.CharField(max_length=50, default='conversions')
    budget = models.CharField(max_length=20, default='medium')
    tone = models.CharField(max_length=20, default='professional')
    analysis_type = models.CharField(max_length=20, choices=[
        ('basic', 'Básico'),
        ('competitive', 'Competitivo')
    ], default='basic')
    ai_response = models.TextField()
    success = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # ✅ AGREGAR ESTE CAMPO NUEVO:
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    additional_data = models.JSONField(blank=True, null=True)  # Para datos extra
    
    def __str__(self):
        return f"{self.product_title} - {self.analysis_type} - {self.created_at.date()}"
    
    class Meta:
        ordering = ['-created_at']
        
    # Tipo de análisis
    analysis_type = models.CharField(
        max_length=20,
        choices=[
            ('basic', 'Análisis Básico'),
            ('competitive', 'Análisis Competitivo')
        ],
        default='basic'
    )
    
    # Respuesta de IA
    ai_response = models.TextField(blank=True)
    
    # Datos adicionales (para análisis competitivo)
    additional_data = models.JSONField(default=dict, blank=True, null=True)
    competitor_analysis = models.JSONField(default=dict, blank=True)
    keywords = models.JSONField(default=list, blank=True)
    estimated_budget = models.CharField(max_length=50, blank=True)
    
    # Métricas de engagement
    strategy_rating = models.IntegerField(null=True, blank=True)
    was_implemented = models.BooleanField(default=False)
    conversion_rate = models.FloatField(null=True, blank=True)
    
    # Usuario (opcional - para sistema de usuarios futuro)
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='analyses'
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['platform', 'created_at']),
            models.Index(fields=['analysis_type', 'success'])
        ]
    
    def __str__(self):
        return f"{self.product_title or 'Producto'} - {self.platform} - {self.created_at}"


# ============= PLANTILLAS DE MARKETING =============
class MarketingTemplate(models.Model):
    """Plantillas predefinidas para diferentes nichos"""
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    platform = models.CharField(max_length=50)
    template_content = models.JSONField()
    success_rate = models.FloatField(default=0.0)
    times_used = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-success_rate', '-times_used']
    
    def __str__(self):
        return f"{self.name} - {self.platform} ({self.success_rate}%)"


# ============= ANÁLISIS DE COMPETIDORES =============
class CompetitorAnalysis(models.Model):
    """Análisis detallado de competidores"""
    analysis = models.ForeignKey(
        AnalysisHistory, 
        on_delete=models.CASCADE,
        related_name='competitors'
    )
    competitor_url = models.URLField()
    competitor_name = models.CharField(max_length=200)
    competitor_price = models.CharField(max_length=50, blank=True)
    strengths = models.JSONField(default=list)
    weaknesses = models.JSONField(default=list)
    strategies = models.JSONField(default=list)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Competidor: {self.competitor_name}"


# ============= SISTEMA DE USUARIOS (OPCIONAL - PARA FUTURO) =============
class UserProfile(models.Model):
    """Perfil extendido para usuarios (cuando implementes autenticación)"""
    PLAN_CHOICES = [
        ('free', 'Plan Gratuito'),
        ('pro', 'Plan Profesional'),
        ('premium', 'Plan Premium'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # Plan y límites
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    plan_expires = models.DateTimeField(null=True, blank=True)
    
    # Límites
    analyses_limit_monthly = models.IntegerField(default=5)
    competitive_analyses_allowed = models.BooleanField(default=False)
    pdf_exports_allowed = models.BooleanField(default=True)
    templates_access = models.BooleanField(default=True)
    api_access = models.BooleanField(default=False)
    
    # Contadores
    analyses_this_month = models.IntegerField(default=0)
    total_analyses = models.IntegerField(default=0)
    last_analysis = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    email_verified = models.BooleanField(default=False)
    
    # Preferencias
    preferred_platform = models.CharField(max_length=50, null=True, blank=True)
    company_name = models.CharField(max_length=200, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_plan_display()}"
    
    def can_analyze(self):
        """Verifica si puede hacer otro análisis"""
        if self.plan == 'premium':
            return True
        return self.analyses_this_month < self.analyses_limit_monthly
    
    def can_analyze_competitive(self):
        """Verifica si puede hacer análisis competitivo"""
        return self.competitive_analyses_allowed
    
    def increment_usage(self, analysis_type='basic'):
        """Incrementa contadores"""
        self.analyses_this_month += 1
        self.total_analyses += 1
        self.last_analysis = timezone.now()
        self.save()
    
    def reset_monthly_usage(self):
        """Resetea contador mensual"""
        self.analyses_this_month = 0
        self.save()
    
    def upgrade_plan(self, new_plan):
        """Actualiza plan"""
        self.plan = new_plan
        
        if new_plan == 'free':
            self.analyses_limit_monthly = 5
            self.competitive_analyses_allowed = False
            self.api_access = False
        elif new_plan == 'pro':
            self.analyses_limit_monthly = 100
            self.competitive_analyses_allowed = True
            self.api_access = False
            self.plan_expires = timezone.now() + timedelta(days=30)
        elif new_plan == 'premium':
            self.analyses_limit_monthly = 999999
            self.competitive_analyses_allowed = True
            self.api_access = True
            self.plan_expires = timezone.now() + timedelta(days=30)
        
        self.save()


class UsageLog(models.Model):
    """Log de uso para analytics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usage_logs')
    action = models.CharField(max_length=50)
    details = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    success = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.created_at}"


class Invitation(models.Model):
    """Sistema de invitaciones"""
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invitations_sent')
    email = models.EmailField()
    code = models.CharField(max_length=20, unique=True)
    accepted = models.BooleanField(default=False)
    accepted_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='invitation_used'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Invitación de {self.inviter.username} a {self.email}"


# ============= SIGNALS =============
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crea perfil automáticamente"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Guarda el perfil"""
    if hasattr(instance, 'profile'):
        instance.profile.save()