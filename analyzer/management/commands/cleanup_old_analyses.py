# analyzer/management/commands/cleanup_old_analyses.py
# COMANDO: python manage.py cleanup_old_analyses

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from analyzer.models import AnalysisHistory

class Command(BaseCommand):
    help = 'Limpia análisis antiguos sin usuario después de X días'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Días para mantener análisis sin usuario (default: 30)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo mostrar qué se eliminaría sin hacerlo'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Análisis sin usuario y antiguos
        old_analyses = AnalysisHistory.objects.filter(
            user__isnull=True,
            created_at__lt=cutoff_date
        )
        
        count = old_analyses.count()
        
        if dry_run:
            self.stdout.write(f"🔍 DRY RUN: Se eliminarían {count} análisis antiguos")
            for analysis in old_analyses[:10]:  # Mostrar solo los primeros 10
                self.stdout.write(f"  - {analysis.product_title} ({analysis.created_at})")
            if count > 10:
                self.stdout.write(f"  ... y {count - 10} más")
        else:
            deleted_count, _ = old_analyses.delete()
            self.stdout.write(
                self.style.SUCCESS(f"✅ Eliminados {deleted_count} análisis antiguos")
            )


# =============================================================================
# analyzer/management/commands/generate_test_data.py
# COMANDO: python manage.py generate_test_data

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from analyzer.models import AnalysisHistory, MarketingTemplate
import random

class Command(BaseCommand):
    help = 'Genera datos de prueba para desarrollo'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=5,
            help='Número de usuarios de prueba a crear'
        )
        parser.add_argument(
            '--analyses',
            type=int,
            default=20,
            help='Número de análisis de prueba a crear'
        )
    
    def handle(self, *args, **options):
        users_count = options['users']
        analyses_count = options['analyses']
        
        self.stdout.write("🚀 Generando datos de prueba...")
        
        # Crear usuarios de prueba
        test_users = []
        for i in range(users_count):
            username = f"testuser{i+1}"
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f"test{i+1}@example.com",
                    password="password123"
                )
                test_users.append(user)
                self.stdout.write(f"👤 Usuario creado: {username}")
        
        # Productos de ejemplo
        test_products = [
            {
                'title': 'Curso de Marketing Digital',
                'price': '$199',
                'url': 'https://example.com/curso-marketing',
                'platform': 'youtube'
            },
            {
                'title': 'Suplemento Proteína Premium',
                'price': '$49.99',
                'url': 'https://example.com/proteina',
                'platform': 'instagram'
            },
            {
                'title': 'Libro de Finanzas Personales',
                'price': '$29.99',
                'url': 'https://example.com/libro-finanzas',
                'platform': 'tiktok'
            },
            {
                'title': 'Software de Productividad',
                'price': '$99/año',
                'url': 'https://example.com/software',
                'platform': 'linkedin'
            },
            {
                'title': 'Ropa Deportiva Eco-Friendly',
                'price': '$79.99',
                'url': 'https://example.com/ropa-deportiva',
                'platform': 'facebook'
            }
        ]
        
        # Crear análisis de prueba
        for i in range(analyses_count):
            product = random.choice(test_products)
            user = random.choice(test_users) if test_users else None
            
            analysis = AnalysisHistory.objects.create(
                user=user,
                product_url=product['url'],
                product_title=product['title'],
                product_price=product['price'],
                product_description=f"Descripción del producto {product['title']}",
                platform=product['platform'],
                target_audience=random.choice([
                    'mujeres 25-35 años',
                    'hombres 18-25 años',
                    'profesionales 30-45 años',
                    'estudiantes universitarios',
                    'padres de familia'
                ]),
                campaign_goal=random.choice(['conversions', 'awareness', 'engagement']),
                budget=random.choice(['low', 'medium', 'high']),
                tone=random.choice(['professional', 'casual', 'funny']),
                analysis_type=random.choice(['basic', 'competitive']),
                ai_response=f"""
                ## Estrategia para {product['title']}
                
                ### Análisis del Producto
                Este producto tiene gran potencial en {product['platform']}.
                
                ### Público Objetivo
                Dirigido a personas interesadas en mejoras profesionales y personales.
                
                ### Estrategia de Contenido
                1. Videos cortos mostrando beneficios
                2. Testimonios de usuarios reales
                3. Comparaciones con alternativas
                
                ### Call to Action
                "¡Transforma tu vida HOY! Link en bio 👆"
                
                ### Hashtags Recomendados
                #marketing #productividad #exito #motivacion
                """,
                success=True
            )
            
            self.stdout.write(f"📊 Análisis creado: {product['title']}")
        
        self.stdout.write(
            self.style.SUCCESS(f"✅ Datos de prueba generados: {users_count} usuarios, {analyses_count} análisis")
        )


# =============================================================================
# analyzer/management/commands/export_analytics.py
# COMANDO: python manage.py export_analytics

from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from analyzer.models import AnalysisHistory
import json
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Exporta analytics de la aplicación'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            choices=['json', 'csv'],
            default='json',
            help='Formato de exportación'
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Archivo de salida (opcional)'
        )
    
    def handle(self, *args, **options):
        format_type = options['format']
        output_file = options['output']
        
        self.stdout.write("📈 Generando analytics...")
        
        # Obtener estadísticas
        total_analyses = AnalysisHistory.objects.count()
        successful_analyses = AnalysisHistory.objects.filter(success=True).count()
        
        # Estadísticas por plataforma
        platform_stats = AnalysisHistory.objects.values('platform').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Estadísticas por tipo
        type_stats = AnalysisHistory.objects.values('analysis_type').annotate(
            count=Count('id')
        )
        
        # Análisis por mes (últimos 6 meses)
        monthly_stats = []
        for i in range(6):
            date = datetime.now() - timedelta(days=30*i)
            start_date = date.replace(day=1)
            if i > 0:
                end_date = (datetime.now() - timedelta(days=30*(i-1))).replace(day=1)
            else:
                end_date = datetime.now()
            
            count = AnalysisHistory.objects.filter(
                created_at__gte=start_date,
                created_at__lt=end_date
            ).count()
            
            monthly_stats.append({
                'month': start_date.strftime('%Y-%m'),
                'analyses': count
            })
        
        analytics_data = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_analyses': total_analyses,
                'successful_analyses': successful_analyses,
                'success_rate': f"{(successful_analyses/total_analyses*100):.1f}%" if total_analyses > 0 else "0%"
            },
            'platform_stats': list(platform_stats),
            'type_stats': list(type_stats),
            'monthly_trend': monthly_stats
        }
        
        if format_type == 'json':
            output = json.dumps(analytics_data, indent=2, ensure_ascii=False)
        else:  # CSV
            output = self.convert_to_csv(analytics_data)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output)
            self.stdout.write(f"✅ Analytics exportado a: {output_file}")
        else:
            self.stdout.write(output)
    
    def convert_to_csv(self, data):
        """Convierte datos a formato CSV básico"""
        lines = ["Metric,Value"]
        lines.append(f"Total Analyses,{data['summary']['total_analyses']}")
        lines.append(f"Successful Analyses,{data['summary']['successful_analyses']}")
        lines.append(f"Success Rate,{data['summary']['success_rate']}")
        
        lines.append("\nPlatform,Count")
        for stat in data['platform_stats']:
            lines.append(f"{stat['platform']},{stat['count']}")
        
        return "\n".join(lines)


# =============================================================================
# analyzer/management/commands/maintenance_mode.py
# COMANDO: python manage.py maintenance_mode on|off

from django.core.management.base import BaseCommand
from django.core.cache import cache

class Command(BaseCommand):
    help = 'Activa o desactiva el modo de mantenimiento'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['on', 'off'],
            help='Activar (on) o desactivar (off) mantenimiento'
        )
        parser.add_argument(
            '--message',
            type=str,
            default='Sitio en mantenimiento. Vuelve pronto.',
            help='Mensaje a mostrar durante mantenimiento'
        )
    
    def handle(self, *args, **options):
        action = options['action']
        message = options['message']
        
        if action == 'on':
            cache.set('maintenance_mode', True, None)  # Sin expiración
            cache.set('maintenance_message', message, None)
            self.stdout.write(
                self.style.WARNING("🚧 Modo de mantenimiento ACTIVADO")
            )
        else:
            cache.delete('maintenance_mode')
            cache.delete('maintenance_message')
            self.stdout.write(
                self.style.SUCCESS("✅ Modo de mantenimiento DESACTIVADO")
            )


# =============================================================================
# analyzer/management/commands/update_templates.py
# COMANDO: python manage.py update_templates

from django.core.management.base import BaseCommand
from analyzer.models import MarketingTemplate

class Command(BaseCommand):
    help = 'Actualiza plantillas de marketing con nuevos datos'
    
    def handle(self, *args, **options):
        self.stdout.write("🔄 Actualizando plantillas de marketing...")
        
        # Plantillas por defecto
        default_templates = [
            {
                'name': 'Review Tech YouTube',
                'platform': 'youtube',
                'category': 'technology',
                'template': 'Hey! Hoy te traigo un review HONESTO de [PRODUCTO]. ¿Vale la pena? Te cuento todo...',
                'success_rate': 85,
                'times_used': 45
            },
            {
                'name': 'Instagram Lifestyle',
                'platform': 'instagram',
                'category': 'lifestyle',
                'template': '✨ Descubrí [PRODUCTO] y mi vida cambió. Te cuento por qué en mi stories 👆',
                'success_rate': 92,
                'times_used': 78
            },
            {
                'name': 'TikTok Viral Product',
                'platform': 'tiktok',
                'category': 'viral',
                'template': 'POV: Probaste [PRODUCTO] y ahora entiendes el hype 😱 #viral #producto',
                'success_rate': 88,
                'times_used': 156
            },
            {
                'name': 'Facebook Problem-Solution',
                'platform': 'facebook',
                'category': 'problem_solving',
                'template': '¿Cansado de [PROBLEMA]? [PRODUCTO] es la solución que estabas buscando. Te explico:',
                'success_rate': 76,
                'times_used': 34
            },
            {
                'name': 'LinkedIn Professional',
                'platform': 'linkedin',
                'category': 'professional',
                'template': 'Como profesional, [PRODUCTO] ha optimizado mi productividad. Aquí mi análisis:',
                'success_rate': 81,
                'times_used': 23
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for template_data in default_templates:
            template, created = MarketingTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(f"✅ Plantilla creada: {template.name}")
            else:
                # Actualizar datos existentes
                for key, value in template_data.items():
                    setattr(template, key, value)
                template.save()
                updated_count += 1
                self.stdout.write(f"🔄 Plantilla actualizada: {template.name}")
        
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Plantillas procesadas: {created_count} creadas, {updated_count} actualizadas"
            )
        )