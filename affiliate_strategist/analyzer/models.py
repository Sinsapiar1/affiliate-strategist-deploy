# analyzer/models.py - MODELOS AVANZADOS Y COMPLETOS

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime, timedelta
import json
import uuid

# ✅ MODELO PRINCIPAL DE ANÁLISIS (MEJORADO)
class AnalysisHistory(models.Model):
    """Historial de análisis con campos expandidos"""
    
    PLATFORM_CHOICES = [
        ('tiktok', 'TikTok'),
        ('instagram', 'Instagram'),
        ('youtube', 'YouTube'),
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('linkedin', 'LinkedIn'),
        ('pinterest', 'Pinterest'),
        ('snapchat', 'Snapchat'),
    ]
    
    ANALYSIS_TYPE_CHOICES = [
        ('basic', 'Básico'),
        ('competitive', 'Competitivo'),
        ('batch', 'En Lote'),
        ('advanced', 'Avanzado'),
    ]
    
    CAMPAIGN_GOAL_CHOICES = [
        ('conversions', 'Conversiones'),
        ('awareness', 'Conocimiento de Marca'),
        ('engagement', 'Engagement'),
        ('traffic', 'Tráfico Web'),
        ('leads', 'Generación de Leads'),
        ('sales', 'Ventas Directas'),
    ]
    
    BUDGET_CHOICES = [
        ('low', 'Bajo (< $500)'),
        ('medium', 'Medio ($500-2000)'),
        ('high', 'Alto ($2000-5000)'),
        ('enterprise', 'Empresarial (> $5000)'),
    ]
    
    TONE_CHOICES = [
        ('professional', 'Profesional'),
        ('casual', 'Casual'),
        ('funny', 'Divertido'),
        ('educational', 'Educativo'),
        ('inspirational', 'Inspiracional'),
        ('urgent', 'Urgente'),
    ]
    
    # ✅ CAMPOS BÁSICOS
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='analyses')
    
    # ✅ INFORMACIÓN DEL PRODUCTO
    product_url = models.URLField(max_length=500)
    product_title = models.CharField(max_length=300)
    product_price = models.CharField(max_length=100, blank=True, null=True)
    product_description = models.TextField(blank=True, null=True)
    product_category = models.CharField(max_length=100, blank=True, null=True)
    product_brand = models.CharField(max_length=100, blank=True, null=True)
    product_rating = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(5)])
    
    # ✅ CONFIGURACIÓN DE CAMPAÑA
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    target_audience = models.CharField(max_length=300)
    additional_context = models.TextField(blank=True, null=True)
    campaign_goal = models.CharField(max_length=20, choices=CAMPAIGN_GOAL_CHOICES, default='conversions')
    budget = models.CharField(max_length=20, choices=BUDGET_CHOICES, default='medium')
    tone = models.CharField(max_length=20, choices=TONE_CHOICES, default='professional')
    
    # ✅ ANÁLISIS Y RESULTADOS
    analysis_type = models.CharField(max_length=20, choices=ANALYSIS_TYPE_CHOICES, default='basic')
    ai_response = models.TextField()
    ai_model_used = models.CharField(max_length=50, default='gemini-pro')
    processing_time = models.FloatField(null=True, blank=True)  # Tiempo en segundos
    
    # ✅ ESTADO Y MÉTRICAS
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)
    quality_score = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(10)])
    user_rating = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # ✅ METADATOS
    additional_data = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    
    # ✅ TIMESTAMPS
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_reset_date = models.DateField(default=timezone.now, help_text='Fecha del último reset del contador mensual')
    
    # ✅ COMPARTIR Y PRIVACIDAD
    is_public = models.BooleanField(default=False)
    share_token = models.CharField(max_length=32, unique=True, null=True, blank=True)
    views_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['platform', 'success']),
            models.Index(fields=['analysis_type', '-created_at']),
            models.Index(fields=['is_public', 'success']),
        ]
        verbose_name = 'Análisis'
        verbose_name_plural = 'Análisis'
        

    def reset_monthly_counter_if_needed(self):
        """Resetea el contador mensual si ha pasado un mes"""
        from django.utils import timezone
        
        now = timezone.now()
        
        if not hasattr(self, 'last_reset_date') or not self.last_reset_date:
            self.last_reset_date = self.created_at.date() if self.created_at else now.date()
            self.save(update_fields=['last_reset_date'])
            return
        
        if (now.year > self.last_reset_date.year or 
            (now.year == self.last_reset_date.year and now.month > self.last_reset_date.month)):
            
            self.analyses_this_month = 0
            self.last_reset_date = now.date()
            self.save(update_fields=['analyses_this_month', 'last_reset_date'])

    def add_analysis_count(self):
        """Incrementa el contador de análisis del mes"""
        self.reset_monthly_counter_if_needed()
        self.analyses_this_month += 1
        self.total_analyses += 1
        self.save(update_fields=['analyses_this_month', 'total_analyses'])
    
    def __str__(self):
        return f"{self.product_title} - {self.analysis_type} ({self.created_at.date()})"
    
    def save(self, *args, **kwargs):
        if not self.share_token:
            self.share_token = uuid.uuid4().hex[:32]
        super().save(*args, **kwargs)
    
    @property
    def is_recent(self):
        """Verifica si el análisis es reciente (últimas 24 horas)"""
        return self.created_at >= timezone.now() - timedelta(hours=24)
    
    @property
    def age_in_days(self):
        """Edad del análisis en días"""
        return (timezone.now() - self.created_at).days
    
    def get_share_url(self):
        """URL para compartir el análisis"""
        return f"/share/{self.share_token}/"


# ✅ PLANTILLAS DE MARKETING MEJORADAS
class MarketingTemplate(models.Model):
    """Plantillas de marketing con métricas de rendimiento"""
    
    CATEGORY_CHOICES = [
        ('technology', 'Tecnología'),
        ('lifestyle', 'Estilo de Vida'),
        ('fitness', 'Fitness'),
        ('fashion', 'Moda'),
        ('food', 'Comida'),
        ('travel', 'Viajes'),
        ('education', 'Educación'),
        ('business', 'Negocios'),
        ('health', 'Salud'),
        ('beauty', 'Belleza'),
        ('gaming', 'Gaming'),
        ('general', 'General'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    platform = models.CharField(max_length=20, choices=AnalysisHistory.PLATFORM_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    
    # ✅ CONTENIDO DE LA PLANTILLA
    template = models.TextField(help_text="Usa [PRODUCTO], [PRECIO], [BENEFICIO] como placeholders")
    description = models.TextField(blank=True, null=True)
    hashtags = models.CharField(max_length=500, blank=True, null=True)
    
    # ✅ MÉTRICAS DE RENDIMIENTO
    success_rate = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    times_used = models.PositiveIntegerField(default=0)
    avg_engagement = models.FloatField(default=0)
    avg_conversion_rate = models.FloatField(default=0)
    
    # ✅ METADATOS
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_reset_date = models.DateField(default=timezone.now, help_text='Fecha del último reset del contador mensual')
    
    class Meta:
        ordering = ['-success_rate', '-times_used']
        indexes = [
            models.Index(fields=['platform', 'category', 'is_active']),
            models.Index(fields=['success_rate', '-times_used']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.platform})"
    
    def increment_usage(self):
        """Incrementa contador de uso"""
        self.times_used += 1
        self.save(update_fields=['times_used'])


# ✅ PERFIL DE USUARIO EXTENDIDO
class UserProfile(models.Model):
    """Perfil extendido del usuario con estadísticas"""
    
    PLAN_CHOICES = [
        ('free', 'Gratuito'),
        ('pro', 'Profesional'),
        ('premium', 'Premium'),
        ('enterprise', 'Empresarial'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # ✅ INFORMACIÓN PERSONAL
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    company_name = models.CharField(max_length=200, blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    
    # ✅ UBICACIÓN
    country = models.CharField(max_length=100, blank=True, null=True)
    timezone = models.CharField(max_length=50, default='UTC')
    
    # ✅ PLAN Y LÍMITES
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    plan_expires = models.DateTimeField(null=True, blank=True)
    analyses_limit_monthly = models.PositiveIntegerField(default=5)
    analyses_this_month = models.PositiveIntegerField(default=0)
    
    # ✅ PREFERENCIAS
    preferred_platforms = models.JSONField(default=list, blank=True)
    default_tone = models.CharField(max_length=20, choices=AnalysisHistory.TONE_CHOICES, default='professional')
    email_notifications = models.BooleanField(default=True)
    
    # ✅ ESTADÍSTICAS
    total_analyses = models.PositiveIntegerField(default=0)
    successful_analyses = models.PositiveIntegerField(default=0)
    avg_quality_score = models.FloatField(default=0)
    
    # ✅ GAMIFICACIÓN
    points = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    achievements = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_reset_date = models.DateField(default=timezone.now, help_text='Fecha del último reset del contador mensual')
    
    class Meta:
        indexes = [
            models.Index(fields=['plan', 'plan_expires']),
            models.Index(fields=['points', 'level']),
        ]
    def reset_monthly_counter_if_needed(self):
     """Método temporal - previene errores"""
    pass
    
    def __str__(self):
        return f"{self.user.username} - {self.get_plan_display()}"
    
    
    def get_plan_display_with_emoji(self):
        """Retorna el plan con emoji"""
        emojis = {
            'free': '🆓',
            'pro': '⭐',
            'premium': '💎',
            'enterprise': '🏢'
        }
        return f"{emojis.get(self.plan, '')} {self.get_plan_display()}"
    
    @property
    def analyses_remaining(self):
        """Análisis restantes este mes"""
        return max(0, self.analyses_limit_monthly - self.analyses_this_month)
    
    @property
    def success_rate(self):
        """Tasa de éxito en porcentaje"""
        if self.total_analyses == 0:
            return 0
        return round((self.successful_analyses / self.total_analyses) * 100, 1)
    
    def can_analyze(self):
        """Verifica si puede hacer más análisis"""
        if self.plan == 'premium':
            return True  # Ilimitado
        return self.analyses_remaining > 0
    
    def add_points(self, points):
        """Añade puntos y calcula nivel"""
        self.points += points
        new_level = min(100, (self.points // 1000) + 1)  # 1000 puntos por nivel
        if new_level > self.level:
            self.level = new_level
            # Trigger achievement
            self.add_achievement(f'level_{new_level}')
        self.save()
    
    def add_achievement(self, achievement_id):
        """Añade logro si no lo tiene"""
        if achievement_id not in self.achievements:
            self.achievements.append(achievement_id)
            self.save(update_fields=['achievements'])
    
    def upgrade_plan(self, new_plan, duration_days=30):
        """Actualiza plan del usuario"""
        plan_limits = {
            'free': 5,
            'pro': 100,
            'premium': 999999,
            'enterprise': 999999
        }
        
        self.plan = new_plan
        self.analyses_limit_monthly = plan_limits.get(new_plan, 5)
        
        if new_plan != 'free':
            self.plan_expires = timezone.now() + timedelta(days=duration_days)
        else:
            self.plan_expires = None
        
        self.save()

    # ✅ AGREGAR ESTOS NUEVOS MÉTODOS:
        
    def reset_monthly_counter_if_needed(self):
        """
        Resetea el contador mensual si ha pasado un mes
        """
        from django.utils import timezone
        from datetime import datetime
        
        now = timezone.now()
        
        # Si no hay fecha de último reset, usar la fecha de creación
        if not hasattr(self, 'last_reset_date') or not self.last_reset_date:
            self.last_reset_date = self.created_at.date() if self.created_at else now.date()
            self.save(update_fields=['last_reset_date'])
            return
        
        # Si ha pasado un mes desde el último reset
        if (now.year > self.last_reset_date.year or 
            (now.year == self.last_reset_date.year and now.month > self.last_reset_date.month)):
            
            self.analyses_this_month = 0
            self.last_reset_date = now.date()
            self.save(update_fields=['analyses_this_month', 'last_reset_date'])
            
            print(f"💫 Contador mensual reseteado para usuario {self.user.username}")

    def add_analysis_count(self):
        """
        Incrementa el contador de análisis del mes
        """
        self.reset_monthly_counter_if_needed()
        self.analyses_this_month += 1
        self.total_analyses += 1
        self.save(update_fields=['analyses_this_month', 'total_analyses'])
    
        def increment_analysis_count(self):
            """Incrementa el contador de análisis del mes"""
            self.reset_monthly_counter_if_needed()
            self.analyses_this_month += 1
            self.total_analyses += 1
            self.save(update_fields=['analyses_this_month', 'total_analyses'])
        
        def get_plan_details(self):
            """Retorna detalles completos del plan"""
            plans = {
                'free': {
                    'name': 'Gratuito',
                    'emoji': '🆓',
                    'monthly_limit': 5,
                    'features': [
                        '5 análisis básicos por mes',
                        'Descarga de PDF',
                        'Historial básico'
                    ],
                    'restrictions': [
                        'Sin análisis competitivos',
                        'Sin prioridad en procesamiento',
                        'Sin soporte premium'
                    ]
                },
                'pro': {
                    'name': 'Profesional',
                    'emoji': '⭐',
                    'monthly_limit': 100,
                    'features': [
                        '100 análisis por mes',
                        'Análisis competitivos ilimitados',
                        'Plantillas premium',
                        'Soporte prioritario'
                    ],
                    'restrictions': []
                },
                'premium': {
                    'name': 'Premium',
                    'emoji': '💎',
                    'monthly_limit': 999999,  # Ilimitado
                    'features': [
                        'Análisis ILIMITADOS',
                        'Todas las funcionalidades',
                        'API Access',
                        'Soporte 24/7'
                    ],
                    'restrictions': []
                }
            }
            return plans.get(self.plan, plans['free'])

# ✅ SISTEMA DE FEEDBACK Y RATING
class AnalysisFeedback(models.Model):
    """Feedback de usuarios sobre análisis"""
    
    FEEDBACK_TYPE_CHOICES = [
        ('rating', 'Calificación'),
        ('improvement', 'Sugerencia de Mejora'),
        ('bug', 'Reporte de Bug'),
        ('feature', 'Solicitud de Función'),
    ]
    
    analysis = models.ForeignKey(AnalysisHistory, on_delete=models.CASCADE, related_name='feedbacks')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE_CHOICES)
    rating = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    
    # ✅ DETALLES ESPECÍFICOS
    helpful = models.BooleanField(null=True, blank=True)
    accuracy = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    completeness = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['analysis', 'user']  # Un feedback por usuario por análisis
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Feedback de {self.user.username} - {self.analysis.product_title[:50]}"


# ✅ SISTEMA DE FAVORITOS
class FavoriteAnalysis(models.Model):
    """Análisis favoritos de usuarios"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    analysis = models.ForeignKey(AnalysisHistory, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'analysis']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} ♥ {self.analysis.product_title[:50]}"


# ✅ SISTEMA DE NOTIFICACIONES
class Notification(models.Model):
    """Sistema de notificaciones para usuarios"""
    
    NOTIFICATION_TYPES = [
        ('analysis_complete', 'Análisis Completado'),
        ('plan_upgrade', 'Actualización de Plan'),
        ('achievement', 'Logro Desbloqueado'),
        ('system', 'Notificación del Sistema'),
        ('feedback', 'Solicitud de Feedback'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # ✅ ESTADO
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    
    # ✅ DATOS ADICIONALES
    related_analysis = models.ForeignKey(AnalysisHistory, on_delete=models.CASCADE, null=True, blank=True)
    action_url = models.URLField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def mark_as_read(self):
        """Marca como leída"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


# ✅ ANALYTICS Y MÉTRICAS
class DailyMetrics(models.Model):
    """Métricas diarias del sistema"""
    
    date = models.DateField(unique=True)
    
    # ✅ ANÁLISIS
    total_analyses = models.PositiveIntegerField(default=0)
    successful_analyses = models.PositiveIntegerField(default=0)
    failed_analyses = models.PositiveIntegerField(default=0)
    
    # ✅ USUARIOS
    new_users = models.PositiveIntegerField(default=0)
    active_users = models.PositiveIntegerField(default=0)
    premium_users = models.PositiveIntegerField(default=0)
    
    # ✅ PLATAFORMAS
    platform_breakdown = models.JSONField(default=dict)
    
    # ✅ RENDIMIENTO
    avg_processing_time = models.FloatField(default=0)
    avg_quality_score = models.FloatField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"Métricas {self.date}"


# ✅ SIGNALS PARA AUTOMATIZACIÓN
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crea perfil automáticamente al registrarse"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Guarda perfil al actualizar usuario"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=AnalysisHistory)
def update_user_stats(sender, instance, created, **kwargs):
    """Actualiza estadísticas del usuario al crear análisis"""
    if created and instance.user:
        profile = instance.user.profile
        profile.total_analyses += 1
        profile.analyses_this_month += 1
        
        if instance.success:
            profile.successful_analyses += 1
            profile.add_points(10)  # 10 puntos por análisis exitoso
        
        profile.save()