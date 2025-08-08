# analyzer/api/serializers.py - SERIALIZERS PARA REST API

from rest_framework import serializers
from django.contrib.auth.models import User
from analyzer.models import (
    AnalysisHistory, MarketingTemplate, UserProfile, 
    AnalysisFeedback, FavoriteAnalysis, Notification
)

class UserSerializer(serializers.ModelSerializer):
    """Serializer básico de usuario"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer del perfil de usuario"""
    
    plan_display = serializers.CharField(source='get_plan_display_with_emoji', read_only=True)
    analyses_remaining = serializers.IntegerField(read_only=True)
    success_rate = serializers.FloatField(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'bio', 'website', 'company_name', 'job_title', 'country',
            'plan', 'plan_display', 'plan_expires', 'analyses_limit_monthly',
            'analyses_remaining', 'preferred_platforms', 'default_tone',
            'total_analyses', 'successful_analyses', 'success_rate',
            'points', 'level', 'achievements'
        ]
        read_only_fields = [
            'plan', 'plan_expires', 'analyses_limit_monthly', 'total_analyses',
            'successful_analyses', 'points', 'level', 'achievements'
        ]

class AnalysisHistoryListSerializer(serializers.ModelSerializer):
    """Serializer para lista de análisis (campos mínimos)"""
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    age_in_days = serializers.IntegerField(read_only=True)
    is_recent = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = AnalysisHistory
        fields = [
            'id', 'product_title', 'product_price', 'platform', 'platform_display',
            'analysis_type', 'success', 'created_at', 'user_username',
            'age_in_days', 'is_recent', 'views_count', 'is_public'
        ]

class AnalysisHistoryDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para análisis individual"""
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    campaign_goal_display = serializers.CharField(source='get_campaign_goal_display', read_only=True)
    budget_display = serializers.CharField(source='get_budget_display', read_only=True)
    tone_display = serializers.CharField(source='get_tone_display', read_only=True)
    share_url = serializers.CharField(source='get_share_url', read_only=True)
    age_in_days = serializers.IntegerField(read_only=True)
    is_recent = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = AnalysisHistory
        fields = [
            'id', 'product_url', 'product_title', 'product_price', 'product_description',
            'product_category', 'product_brand', 'product_rating',
            'platform', 'platform_display', 'target_audience', 'additional_context',
            'campaign_goal', 'campaign_goal_display', 'budget', 'budget_display',
            'tone', 'tone_display', 'analysis_type', 'ai_response', 'ai_model_used',
            'processing_time', 'success', 'quality_score', 'user_rating',
            'created_at', 'updated_at', 'user_username', 'share_url',
            'age_in_days', 'is_recent', 'views_count', 'is_public'
        ]
        read_only_fields = [
            'id', 'ai_response', 'ai_model_used', 'processing_time', 'success',
            'created_at', 'updated_at', 'share_url', 'views_count'
        ]

class AnalysisCreateSerializer(serializers.Serializer):
    """Serializer para crear análisis via API"""
    
    product_url = serializers.URLField(max_length=500)
    platform = serializers.ChoiceField(choices=AnalysisHistory.PLATFORM_CHOICES)
    target_audience = serializers.CharField(max_length=300)
    additional_context = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    campaign_goal = serializers.ChoiceField(choices=AnalysisHistory.CAMPAIGN_GOAL_CHOICES, default='conversions')
    budget = serializers.ChoiceField(choices=AnalysisHistory.BUDGET_CHOICES, default='medium')
    tone = serializers.ChoiceField(choices=AnalysisHistory.TONE_CHOICES, default='professional')
    analysis_type = serializers.ChoiceField(choices=AnalysisHistory.ANALYSIS_TYPE_CHOICES, default='basic')
    api_key = serializers.CharField(max_length=200, write_only=True)
    
    # Para análisis competitivo
    competitor_urls = serializers.ListField(
        child=serializers.URLField(),
        required=False,
        max_length=5
    )
    
    def validate_product_url(self, value):
        """Valida que la URL sea accesible"""
        import requests
        try:
            response = requests.head(value, timeout=10)
            if response.status_code >= 400:
                raise serializers.ValidationError("URL no accesible")
        except requests.RequestException:
            raise serializers.ValidationError("Error al acceder a la URL")
        
        return value
    
    def validate(self, attrs):
        """Validaciones cruzadas"""
        if attrs.get('analysis_type') == 'competitive':
            if not attrs.get('competitor_urls'):
                raise serializers.ValidationError({
                    'competitor_urls': 'Requerido para análisis competitivo'
                })
        
        return attrs

class MarketingTemplateSerializer(serializers.ModelSerializer):
    """Serializer para plantillas de marketing"""
    
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = MarketingTemplate
        fields = [
            'id', 'name', 'platform', 'platform_display', 'category', 'category_display',
            'template', 'description', 'hashtags', 'success_rate', 'times_used',
            'avg_engagement', 'is_active', 'is_premium', 'created_at'
        ]
        read_only_fields = [
            'id', 'success_rate', 'times_used', 'avg_engagement', 'created_at'
        ]

class AnalysisFeedbackSerializer(serializers.ModelSerializer):
    """Serializer para feedback de análisis"""
    
    class Meta:
        model = AnalysisFeedback
        fields = [
            'id', 'analysis', 'feedback_type', 'rating', 'comment',
            'helpful', 'accuracy', 'completeness', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_rating(self, value):
        """Valida rating según tipo de feedback"""
        if self.initial_data.get('feedback_type') == 'rating' and not value:
            raise serializers.ValidationError("Rating requerido para feedback de tipo 'rating'")
        return value

class NotificationSerializer(serializers.ModelSerializer):
    """Serializer para notificaciones"""
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message', 'is_read',
            'action_url', 'created_at', 'read_at'
        ]
        read_only_fields = ['id', 'created_at', 'read_at']

# =============================================================================
# analyzer/api/views.py - VISTAS REST API

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class StandardResultsSetPagination(PageNumberPagination):
    """Paginación estándar para APIs"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class AnalysisAPIThrottle(UserRateThrottle):
    """Rate limiting específico para análisis"""
    scope = 'analysis'
    rate = '10/hour'  # 10 análisis por hora

class AnalysisHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """API para consultar análisis"""
    
    serializer_class = AnalysisHistoryListSerializer
    pagination_class = StandardResultsSetPagination
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # Filtros disponibles
    filterset_fields = ['platform', 'analysis_type', 'success', 'is_public']
    search_fields = ['product_title', 'product_description', 'target_audience']
    ordering_fields = ['created_at', 'views_count', 'quality_score']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filtra análisis según permisos del usuario"""
        queryset = AnalysisHistory.objects.select_related('user')
        
        if self.request.user.is_authenticated:
            # Usuario autenticado ve sus análisis y los públicos
            queryset = queryset.filter(
                Q(user=self.request.user) | Q(is_public=True)
            )
        else:
            # Usuario anónimo solo ve análisis públicos
            queryset = queryset.filter(is_public=True)
        
        return queryset
    
    def get_serializer_class(self):
        """Usa serializer detallado para vista individual"""
        if self.action == 'retrieve':
            return AnalysisHistoryDetailSerializer
        return AnalysisHistoryListSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """Incrementa contador de vistas al ver análisis"""
        instance = self.get_object()
        
        # Incrementar views solo si no es el propietario
        if not request.user.is_authenticated or instance.user != request.user:
            instance.views_count += 1
            instance.save(update_fields=['views_count'])
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_analyses(self, request):
        """Endpoint para obtener solo los análisis del usuario actual"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        queryset = self.filter_queryset(
            AnalysisHistory.objects.filter(user=request.user)
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estadísticas de análisis"""
        queryset = self.get_queryset()
        
        # Estadísticas básicas
        total = queryset.count()
        successful = queryset.filter(success=True).count()
        
        # Por plataforma
        platform_stats = queryset.values('platform').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Por tipo
        type_stats = queryset.values('analysis_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Tendencia últimos 7 días
        last_week = timezone.now() - timedelta(days=7)
        daily_stats = []
        for i in range(7):
            date = last_week + timedelta(days=i)
            count = queryset.filter(
                created_at__date=date.date()
            ).count()
            daily_stats.append({
                'date': date.date().isoformat(),
                'count': count
            })
        
        return Response({
            'summary': {
                'total': total,
                'successful': successful,
                'success_rate': round((successful / total * 100), 1) if total > 0 else 0
            },
            'by_platform': list(platform_stats),
            'by_type': list(type_stats),
            'daily_trend': daily_stats
        })

class AnalysisCreateAPIView(APIView):
    """API para crear análisis"""
    
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AnalysisAPIThrottle]
    
    def post(self, request):
        """Crea nuevo análisis"""
        serializer = AnalysisCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar límites del usuario
        if not request.user.profile.can_analyze():
            return Response(
                {'error': 'Has alcanzado el límite de análisis para tu plan'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        try:
            # Procesar análisis
            from analyzer.views import AffiliateStrategistView
            from django.http import HttpRequest
            
            # Simular request POST
            analysis_request = HttpRequest()
            analysis_request.method = 'POST'
            analysis_request.user = request.user
            analysis_request.POST = serializer.validated_data
            
            # Usar la vista existente para procesar
            view = AffiliateStrategistView()
            
            if serializer.validated_data['analysis_type'] == 'competitive':
                response = view.competitive_analysis(analysis_request)
            else:
                response = view.basic_analysis(analysis_request)
            
            # Convertir JsonResponse a Response de DRF
            response_data = json.loads(response.content)
            
            if response_data.get('success'):
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    response_data, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"API analysis error: {str(e)}")
            return Response(
                {'error': 'Error interno al procesar análisis'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MarketingTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """API para plantillas de marketing"""
    
    queryset = MarketingTemplate.objects.filter(is_active=True)
    serializer_class = MarketingTemplateSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['platform', 'category', 'is_premium']
    search_fields = ['name', 'template', 'description']
    ordering_fields = ['success_rate', 'times_used', 'created_at']
    ordering = ['-success_rate']
    
    def get_queryset(self):
        """Filtra plantillas según plan del usuario"""
        queryset = super().get_queryset()
        
        if self.request.user.is_authenticated:
            # Si es usuario premium, ver todas las plantillas
            if self.request.user.profile.plan in ['premium', 'enterprise']:
                return queryset
            # Usuarios gratuitos/pro no ven plantillas premium
            return queryset.filter(is_premium=False)
        
        # Usuarios anónimos solo ven plantillas gratuitas
        return queryset.filter(is_premium=False)
    
    @action(detail=True, methods=['post'])
    def use_template(self, request, pk=None):
        """Marca plantilla como usada"""
        template = self.get_object()
        template.increment_usage()
        
        return Response({
            'message': 'Template usage recorded',
            'times_used': template.times_used
        })

class UserProfileAPIView(APIView):
    """API para perfil de usuario"""
    
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Obtiene perfil del usuario actual"""
        serializer = UserProfileSerializer(request.user.profile)
        return Response(serializer.data)
    
    def patch(self, request):
        """Actualiza perfil del usuario"""
        serializer = UserProfileSerializer(
            request.user.profile, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )

class AnalysisFeedbackViewSet(viewsets.ModelViewSet):
    """API para feedback de análisis"""
    
    serializer_class = AnalysisFeedbackSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Solo feedback del usuario actual"""
        return AnalysisFeedback.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Asigna usuario actual al crear feedback"""
        serializer.save(user=self.request.user)

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """API para notificaciones del usuario"""
    
    serializer_class = NotificationSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Solo notificaciones del usuario actual"""
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['patch'])
    def mark_as_read(self, request, pk=None):
        """Marca notificación como leída"""
        notification = self.get_object()
        notification.mark_as_read()
        
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch'])
    def mark_all_read(self, request):
        """Marca todas las notificaciones como leídas"""
        updated = self.get_queryset().filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return Response({
            'message': f'{updated} notifications marked as read'
        })

# =============================================================================
# analyzer/api/urls.py - URLs DE LA API

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    AnalysisHistoryViewSet, AnalysisCreateAPIView, MarketingTemplateViewSet,
    UserProfileAPIView, AnalysisFeedbackViewSet, NotificationViewSet
)

# Router para ViewSets
router = DefaultRouter()
router.register(r'analyses', AnalysisHistoryViewSet, basename='analysis')
router.register(r'templates', MarketingTemplateViewSet)
router.register(r'feedback', AnalysisFeedbackViewSet, basename='feedback')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    # Auth
    path('auth/token/', obtain_auth_token, name='api_token_auth'),
    
    # Main API routes
    path('', include(router.urls)),
    
    # Custom endpoints
    path('analyze/', AnalysisCreateAPIView.as_view(), name='api_analyze'),
    path('profile/', UserProfileAPIView.as_view(), name='api_profile'),
    
    # API documentation (si usas drf-spectacular)
    # path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
