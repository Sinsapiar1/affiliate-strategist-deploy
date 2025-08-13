# analyzer/monitoring/metrics.py - SISTEMA DE MÉTRICAS Y MONITORING

import logging
import time
import psutil
import threading
from datetime import datetime, timedelta
from django.core.cache import cache
from django.db.models import Count, Avg, Q
from django.utils import timezone
from django.conf import settings
from analyzer.models import AnalysisHistory, UserProfile, DailyMetrics
from collections import defaultdict
import json

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Recolector de métricas del sistema"""
    
    def __init__(self):
        self.metrics_cache = defaultdict(list)
        self.start_time = time.time()
        self.lock = threading.Lock()
    
    def record_analysis_time(self, analysis_type, processing_time):
        """Registra tiempo de procesamiento de análisis"""
        with self.lock:
            self.metrics_cache[f'analysis_time_{analysis_type}'].append(processing_time)
            
            # Mantener solo últimas 1000 métricas
            if len(self.metrics_cache[f'analysis_time_{analysis_type}']) > 1000:
                self.metrics_cache[f'analysis_time_{analysis_type}'] = \
                    self.metrics_cache[f'analysis_time_{analysis_type}'][-1000:]
    
    def record_api_call(self, endpoint, response_time, status_code):
        """Registra llamadas API"""
        metric_key = f'api_{endpoint.replace("/", "_")}'
        
        with self.lock:
            self.metrics_cache[metric_key].append({
                'response_time': response_time,
                'status_code': status_code,
                'timestamp': time.time()
            })
    
    def record_user_action(self, action, user_id=None):
        """Registra acciones de usuario"""
        with self.lock:
            self.metrics_cache['user_actions'].append({
                'action': action,
                'user_id': user_id,
                'timestamp': time.time()
            })
    
    def get_system_metrics(self):
        """Obtiene métricas del sistema"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'disk_percent': disk.percent,
                'disk_free_gb': round(disk.free / (1024**3), 2),
                'uptime_hours': round((time.time() - self.start_time) / 3600, 2)
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {str(e)}")
            return {}
    
    def get_database_metrics(self):
        """Obtiene métricas de la base de datos"""
        try:
            # Métricas básicas
            total_analyses = AnalysisHistory.objects.count()
            successful_analyses = AnalysisHistory.objects.filter(success=True).count()
            total_users = UserProfile.objects.count()
            active_users_24h = UserProfile.objects.filter(
                user__last_login__gte=timezone.now() - timedelta(hours=24)
            ).count()
            
            # Métricas de rendimiento
            avg_processing_time = AnalysisHistory.objects.filter(
                processing_time__isnull=False
            ).aggregate(avg_time=Avg('processing_time'))['avg_time'] or 0
            
            return {
                'total_analyses': total_analyses,
                'successful_analyses': successful_analyses,
                'success_rate': round((successful_analyses / total_analyses * 100), 2) if total_analyses > 0 else 0,
                'total_users': total_users,
                'active_users_24h': active_users_24h,
                'avg_processing_time': round(avg_processing_time, 2)
            }
        except Exception as e:
            logger.error(f"Error getting database metrics: {str(e)}")
            return {}
    
    def get_performance_metrics(self):
        """Obtiene métricas de rendimiento calculadas"""
        with self.lock:
            metrics = {}
            
            # Tiempo promedio de análisis por tipo
            for analysis_type in ['basic', 'competitive']:
                key = f'analysis_time_{analysis_type}'
                if key in self.metrics_cache and self.metrics_cache[key]:
                    times = self.metrics_cache[key]
                    metrics[f'avg_{analysis_type}_time'] = round(sum(times) / len(times), 2)
                    metrics[f'max_{analysis_type}_time'] = round(max(times), 2)
                    metrics[f'min_{analysis_type}_time'] = round(min(times), 2)
            
            # Acciones de usuario por hora
            if 'user_actions' in self.metrics_cache:
                recent_actions = [
                    action for action in self.metrics_cache['user_actions']
                    if time.time() - action['timestamp'] < 3600  # Última hora
                ]
                metrics['actions_per_hour'] = len(recent_actions)
            
            return metrics
    
    def export_metrics_json(self):
        """Exporta todas las métricas en formato JSON"""
        return {
            'timestamp': datetime.now().isoformat(),
            'system': self.get_system_metrics(),
            'database': self.get_database_metrics(),
            'performance': self.get_performance_metrics(),
            'cache_stats': self.get_cache_metrics()
        }
    
    def get_cache_metrics(self):
        """Obtiene métricas del cache"""
        try:
            # Esto depende del backend de cache usado
            return {
                'status': 'active',
                'backend': str(cache.__class__.__name__),
            }
        except Exception as e:
            return {'error': str(e)}

# Instancia global del collector
metrics_collector = MetricsCollector()

class PerformanceMonitor:
    """Monitor de rendimiento y alertas"""
    
    ALERT_THRESHOLDS = {
        'cpu_percent': 90,
        'memory_percent': 85,
        'disk_percent': 90,
        'avg_processing_time': 30,  # segundos
        'error_rate': 10,  # porcentaje
    }
    
    @classmethod
    def check_system_health(cls):
        """Verifica salud del sistema y genera alertas"""
        metrics = metrics_collector.get_system_metrics()
        database_metrics = metrics_collector.get_database_metrics()
        alerts = []
        
        # Verificar CPU
        if metrics.get('cpu_percent', 0) > cls.ALERT_THRESHOLDS['cpu_percent']:
            alerts.append({
                'type': 'HIGH_CPU',
                'message': f"Alto uso de CPU: {metrics['cpu_percent']}%",
                'severity': 'WARNING'
            })
        
        # Verificar memoria
        if metrics.get('memory_percent', 0) > cls.ALERT_THRESHOLDS['memory_percent']:
            alerts.append({
                'type': 'HIGH_MEMORY',
                'message': f"Alto uso de memoria: {metrics['memory_percent']}%",
                'severity': 'WARNING'
            })
        
        # Verificar disco
        if metrics.get('disk_percent', 0) > cls.ALERT_THRESHOLDS['disk_percent']:
            alerts.append({
                'type': 'HIGH_DISK',
                'message': f"Alto uso de disco: {metrics['disk_percent']}%",
                'severity': 'CRITICAL'
            })
        
        # Verificar tiempo de procesamiento
        avg_time = database_metrics.get('avg_processing_time', 0)
        if avg_time > cls.ALERT_THRESHOLDS['avg_processing_time']:
            alerts.append({
                'type': 'SLOW_PROCESSING',
                'message': f"Tiempo de procesamiento lento: {avg_time}s",
                'severity': 'WARNING'
            })
        
        return alerts
    
    @classmethod
    def send_alerts(cls, alerts):
        """Envía alertas (email, Slack, etc.)"""
        for alert in alerts:
            logger.warning(f"ALERT [{alert['severity']}]: {alert['message']}")
            
            # Aquí podrías integrar con servicios externos:
            # - Email notifications
            # - Slack webhooks
            # - PagerDuty
            # - Sentry
            
            if alert['severity'] == 'CRITICAL':
                cls.send_critical_alert(alert)
    
    @classmethod
    def send_critical_alert(cls, alert):
        """Envía alerta crítica inmediata"""
        # Implementar notificación crítica
        logger.critical(f"CRITICAL ALERT: {alert['message']}")

class DailyMetricsCalculator:
    """Calculador de métricas diarias"""
    
    @classmethod
    def calculate_and_store_daily_metrics(cls, date=None):
        """Calcula y almacena métricas diarias"""
        if date is None:
            date = timezone.now().date()
        
        try:
            # Filtrar datos del día
            day_start = timezone.make_aware(datetime.combine(date, datetime.min.time()))
            day_end = day_start + timedelta(days=1)
            
            # Análisis del día
            day_analyses = AnalysisHistory.objects.filter(
                created_at__gte=day_start,
                created_at__lt=day_end
            )
            
            total_analyses = day_analyses.count()
            successful_analyses = day_analyses.filter(success=True).count()
            failed_analyses = total_analyses - successful_analyses
            
            # Usuarios del día
            new_users = UserProfile.objects.filter(
                created_at__gte=day_start,
                created_at__lt=day_end
            ).count()
            
            active_users = UserProfile.objects.filter(
                user__last_login__gte=day_start,
                user__last_login__lt=day_end
            ).count()
            
            premium_users = UserProfile.objects.filter(
                plan__in=['pro', 'premium', 'enterprise']
            ).count()
            
            # Desglose por plataforma
            platform_breakdown = {}
            for platform, _ in AnalysisHistory.PLATFORM_CHOICES:
                count = day_analyses.filter(platform=platform).count()
                if count > 0:
                    platform_breakdown[platform] = count
            
            # Métricas de rendimiento
            processing_times = day_analyses.filter(
                processing_time__isnull=False
            ).values_list('processing_time', flat=True)
            
            avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
            
            quality_scores = day_analyses.filter(
                quality_score__isnull=False
            ).values_list('quality_score', flat=True)
            
            avg_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            # Crear o actualizar métricas diarias
            daily_metrics, created = DailyMetrics.objects.update_or_create(
                date=date,
                defaults={
                    'total_analyses': total_analyses,
                    'successful_analyses': successful_analyses,
                    'failed_analyses': failed_analyses,
                    'new_users': new_users,
                    'active_users': active_users,
                    'premium_users': premium_users,
                    'platform_breakdown': platform_breakdown,
                    'avg_processing_time': avg_processing_time,
                    'avg_quality_score': avg_quality_score,
                }
            )
            
            action = "created" if created else "updated"
            logger.info(f"Daily metrics {action} for {date}")
            
            return daily_metrics
            
        except Exception as e:
            logger.error(f"Error calculating daily metrics: {str(e)}")
            return None

# =============================================================================
# analyzer/monitoring/decorators.py - DECORADORES PARA MONITORING

import time
import functools
from django.http import JsonResponse
from django.conf import settings

def monitor_performance(metric_name=None):
    """Decorador para monitorear rendimiento de funciones"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                processing_time = time.time() - start_time
                
                # Registrar métrica
                name = metric_name or f"{func.__module__}.{func.__name__}"
                metrics_collector.record_analysis_time(name, processing_time)
                
                # Log si es muy lento
                if processing_time > 10:  # 10 segundos
                    logger.warning(f"Slow function {name}: {processing_time:.2f}s")
                
                return result
                
            except Exception as e:
                processing_time = time.time() - start_time
                logger.error(f"Error in {func.__name__}: {str(e)} (took {processing_time:.2f}s)")
                raise
        
        return wrapper
    return decorator

def monitor_api_calls(endpoint_name=None):
    """Decorador para monitorear llamadas API"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            start_time = time.time()
            endpoint = endpoint_name or request.path
            
            try:
                response = func(request, *args, **kwargs)
                response_time = time.time() - start_time
                
                # Registrar métrica API
                status_code = getattr(response, 'status_code', 200)
                metrics_collector.record_api_call(endpoint, response_time, status_code)
                
                return response
                
            except Exception as e:
                response_time = time.time() - start_time
                metrics_collector.record_api_call(endpoint, response_time, 500)
                raise
        
        return wrapper
    return decorator

# =============================================================================
# analyzer/monitoring/dashboard.py - DASHBOARD DE MÉTRICAS

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
import json

@method_decorator(staff_member_required, name='dispatch')
class MetricsDashboardView(View):
    """Dashboard de métricas para administradores"""
    
    def get(self, request):
        """Muestra dashboard de métricas"""
        return render(request, 'analyzer/admin/metrics_dashboard.html')

@staff_member_required
def metrics_api(request):
    """API para obtener métricas en tiempo real"""
    try:
        metrics = metrics_collector.export_metrics_json()
        
        # Agregar alertas actuales
        alerts = PerformanceMonitor.check_system_health()
        metrics['alerts'] = alerts
        
        # Métricas de las últimas 24 horas
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        try:
            today_metrics = DailyMetrics.objects.get(date=today)
            yesterday_metrics = DailyMetrics.objects.get(date=yesterday)
            
            metrics['daily_comparison'] = {
                'today': {
                    'analyses': today_metrics.total_analyses,
                    'success_rate': round((today_metrics.successful_analyses / today_metrics.total_analyses * 100), 1) if today_metrics.total_analyses > 0 else 0,
                    'new_users': today_metrics.new_users
                },
                'yesterday': {
                    'analyses': yesterday_metrics.total_analyses,
                    'success_rate': round((yesterday_metrics.successful_analyses / yesterday_metrics.total_analyses * 100), 1) if yesterday_metrics.total_analyses > 0 else 0,
                    'new_users': yesterday_metrics.new_users
                }
            }
        except DailyMetrics.DoesNotExist:
            metrics['daily_comparison'] = None
        
        return JsonResponse(metrics)
        
    except Exception as e:
        logger.error(f"Error in metrics API: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

# =============================================================================
# analyzer/monitoring/tasks.py - TAREAS PROGRAMADAS

from celery import shared_task
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

@shared_task
def calculate_daily_metrics():
    """Tarea para calcular métricas diarias"""
    try:
        DailyMetricsCalculator.calculate_and_store_daily_metrics()
        logger.info("Daily metrics calculation completed")
    except Exception as e:
        logger.error(f"Error calculating daily metrics: {str(e)}")

@shared_task
def system_health_check():
    """Tarea para verificar salud del sistema"""
    try:
        alerts = PerformanceMonitor.check_system_health()
        if alerts:
            PerformanceMonitor.send_alerts(alerts)
            logger.warning(f"System health check found {len(alerts)} alerts")
        else:
            logger.info("System health check: All systems normal")
    except Exception as e:
        logger.error(f"Error in system health check: {str(e)}")

@shared_task
def cleanup_old_metrics():
    """Limpia métricas antiguas para ahorrar espacio"""
    try:
        # Eliminar métricas de más de 90 días
        cutoff_date = timezone.now().date() - timedelta(days=90)
        deleted_count = DailyMetrics.objects.filter(date__lt=cutoff_date).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} old daily metrics")
    except Exception as e:
        logger.error(f"Error cleaning up metrics: {str(e)}")

# =============================================================================
# analyzer/templates/analyzer/admin/metrics_dashboard.html - TEMPLATE DEL DASHBOARD

"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Métricas - Affiliate Strategist Pro</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .metric-card { transition: transform 0.2s; }
        .metric-card:hover { transform: translateY(-2px); }
        .alert-badge { position: relative; top: -2px; }
    </style>
</head>
<body class="bg-light">
    <div class="container-fluid py-4">
        <!-- Header -->
        <div class="row mb-4">
            <div class="col-12">
                <h1 class="display-6 text-primary">📊 Dashboard de Métricas</h1>
                <p class="text-muted">Monitoreo en tiempo real del sistema</p>
            </div>
        </div>

        <!-- Alertas -->
        <div id="alertsContainer" class="row mb-4" style="display: none;">
            <div class="col-12">
                <div class="alert alert-warning">
                    <h5>⚠️ Alertas del Sistema</h5>
                    <div id="alertsList"></div>
                </div>
            </div>
        </div>

        <!-- Métricas Principales -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card metric-card">
                    <div class="card-body text-center">
                        <h3 id="totalAnalyses" class="text-primary">-</h3>
                        <p class="text-muted">Análisis Totales</p>
                        <small id="analysesChange" class="text-success"></small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card metric-card">
                    <div class="card-body text-center">
                        <h3 id="successRate" class="text-success">-</h3>
                        <p class="text-muted">Tasa de Éxito</p>
                        <small id="successChange" class="text-success"></small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card metric-card">
                    <div class="card-body text-center">
                        <h3 id="activeUsers" class="text-info">-</h3>
                        <p class="text-muted">Usuarios Activos (24h)</p>
                        <small id="usersChange" class="text-success"></small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card metric-card">
                    <div class="card-body text-center">
                        <h3 id="avgProcessingTime" class="text-warning">-</h3>
                        <p class="text-muted">Tiempo Promedio (s)</p>
                        <small id="timeChange" class="text-success"></small>
                    </div>
                </div>
            </div>
        </div>

        <!-- Métricas del Sistema -->
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">💻 Sistema</div>
                    <div class="card-body">
                        <div class="mb-2">
                            <strong>CPU:</strong> <span id="cpuPercent">-</span>%
                            <div class="progress mt-1">
                                <div id="cpuProgress" class="progress-bar"></div>
                            </div>
                        </div>
                        <div class="mb-2">
                            <strong>Memoria:</strong> <span id="memoryPercent">-</span>%
                            <div class="progress mt-1">
                                <div id="memoryProgress" class="progress-bar"></div>
                            </div>
                        </div>
                        <div class="mb-2">
                            <strong>Disco:</strong> <span id="diskPercent">-</span>%
                            <div class="progress mt-1">
                                <div id="diskProgress" class="progress-bar"></div>
                            </div>
                        </div>
                        <div>
                            <strong>Uptime:</strong> <span id="uptime">-</span> horas
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">📈 Análisis por Plataforma</div>
                    <div class="card-body">
                        <canvas id="platformChart" width="400" height="200"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- Gráfico de Tendencias -->
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">📊 Tendencias de Análisis (Últimos 7 días)</div>
                    <div class="card-body">
                        <canvas id="trendsChart" width="400" height="100"></canvas>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
    let platformChart, trendsChart;
    
    // Actualizar métricas cada 30 segundos
    setInterval(updateMetrics, 30000);
    updateMetrics(); // Cargar inicial
    
    async function updateMetrics() {
        try {
            const response = await fetch('/admin/metrics-api/');
            const data = await response.json();
            
            updateMainMetrics(data);
            updateSystemMetrics(data);
            updateAlerts(data.alerts);
            updateCharts(data);
            
        } catch (error) {
            console.error('Error updating metrics:', error);
        }
    }
    
    function updateMainMetrics(data) {
        const db = data.database;
        
        document.getElementById('totalAnalyses').textContent = db.total_analyses || 0;
        document.getElementById('successRate').textContent = (db.success_rate || 0) + '%';
        document.getElementById('activeUsers').textContent = db.active_users_24h || 0;
        document.getElementById('avgProcessingTime').textContent = (db.avg_processing_time || 0) + 's';
        
        // Mostrar cambios si hay comparación diaria
        if (data.daily_comparison) {
            const today = data.daily_comparison.today;
            const yesterday = data.daily_comparison.yesterday;
            
            const analysesChange = today.analyses - yesterday.analyses;
            const usersChange = today.new_users - yesterday.new_users;
            
            document.getElementById('analysesChange').textContent = 
                `${analysesChange >= 0 ? '+' : ''}${analysesChange} vs ayer`;
            document.getElementById('usersChange').textContent = 
                `${usersChange >= 0 ? '+' : ''}${usersChange} nuevos`;
        }
    }
    
    function updateSystemMetrics(data) {
        const sys = data.system;
        
        // CPU
        document.getElementById('cpuPercent').textContent = sys.cpu_percent || 0;
        updateProgressBar('cpuProgress', sys.cpu_percent || 0);
        
        // Memoria
        document.getElementById('memoryPercent').textContent = sys.memory_percent || 0;
        updateProgressBar('memoryProgress', sys.memory_percent || 0);
        
        // Disco
        document.getElementById('diskPercent').textContent = sys.disk_percent || 0;
        updateProgressBar('diskProgress', sys.disk_percent || 0);
        
        // Uptime
        document.getElementById('uptime').textContent = sys.uptime_hours || 0;
    }
    
    function updateProgressBar(id, percentage) {
        const bar = document.getElementById(id);
        bar.style.width = percentage + '%';
        
        // Cambiar color según porcentaje
        bar.className = 'progress-bar';
        if (percentage > 80) bar.classList.add('bg-danger');
        else if (percentage > 60) bar.classList.add('bg-warning');
        else bar.classList.add('bg-success');
    }
    
    function updateAlerts(alerts) {
        const container = document.getElementById('alertsContainer');
        const list = document.getElementById('alertsList');
        
        if (alerts && alerts.length > 0) {
            container.style.display = 'block';
            list.innerHTML = alerts.map(alert => 
                `<div class="alert alert-${alert.severity.toLowerCase() === 'critical' ? 'danger' : 'warning'} alert-sm">
                    ${alert.message}
                </div>`
            ).join('');
        } else {
            container.style.display = 'none';
        }
    }
    
    function updateCharts(data) {
        // Implementar actualización de gráficos
        // Chart.js code aquí
    }
    </script>
</body>
</html>
"""