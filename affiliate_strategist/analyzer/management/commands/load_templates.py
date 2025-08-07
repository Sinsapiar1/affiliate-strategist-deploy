# analyzer/management/commands/load_templates.py

from django.core.management.base import BaseCommand
from analyzer.models import MarketingTemplate

class Command(BaseCommand):
    help = 'Carga plantillas iniciales de marketing'

    def handle(self, *args, **options):
        templates = [
            {
                'name': 'Review Tech YouTube',
                'category': 'tecnologia',
                'platform': 'youtube',
                'template_content': {
                    'hook': '¿Vale la pena {product} en 2024? Mi experiencia después de 30 días',
                    'structure': [
                        '0:00 - Intro: El problema que resuelve',
                        '0:30 - Unboxing y primeras impresiones',
                        '2:00 - Configuración paso a paso',
                        '3:00 - Pruebas de rendimiento reales',
                        '5:00 - Lo bueno y lo malo (honesto)',
                        '7:00 - ¿Para quién es este producto?',
                        '8:00 - Veredicto final y alternativas'
                    ],
                    'cta': '⬇️ LINK DE COMPRA CON DESCUENTO EXCLUSIVO EN LA DESCRIPCIÓN ⬇️',
                    'tips': 'Usa b-roll dinámico, muestra el producto en uso real'
                },
                'success_rate': 85.5
            },
            {
                'name': 'Instagram Lifestyle',
                'category': 'lifestyle',
                'platform': 'instagram',
                'template_content': {
                    'hook': 'El secreto que transformó mi {routine} en solo 2 semanas',
                    'carrusel': [
                        'Slide 1: Foto antes/después o problema relatable',
                        'Slide 2: Introduce el producto como solución',
                        'Slide 3: Cómo lo uso día a día (foto real)',
                        'Slide 4: 3 beneficios principales',
                        'Slide 5: Resultado o testimonio',
                        'Slide 6: CTA con código de descuento'
                    ],
                    'copy': 'Si también estás cansada de {problema}, tienes que ver esto...',
                    'hashtags': ['#LifestyleChange', '#ProductReview', '#RealResults'],
                    'cta': 'Desliza para ver mi transformación → Link en bio con 20% OFF'
                },
                'success_rate': 78.3
            },
            {
                'name': 'TikTok Viral Product',
                'category': 'general',
                'platform': 'tiktok',
                'template_content': {
                    'hook': 'POV: Encuentras el producto que todos buscan en TikTok',
                    'script': [
                        '0-3s: Hook visual impactante',
                        '3-8s: Mostrar el problema de forma divertida',
                        '8-15s: Reveal del producto',
                        '15-25s: 3 formas creativas de usarlo',
                        '25-30s: CTA rápido'
                    ],
                    'audio': 'Usa trending sounds relacionados',
                    'cta': 'Comenta "LINK" para el descuento',
                    'tips': 'Graba vertical, iluminación natural, edición rápida'
                },
                'success_rate': 82.7
            },
            {
                'name': 'Facebook Madres 35+',
                'category': 'hogar',
                'platform': 'facebook',
                'template_content': {
                    'hook': 'Mamás: Este {product} me devolvió 2 horas al día',
                    'estructura': [
                        'Párrafo 1: Historia personal relatable',
                        'Párrafo 2: Cómo descubrí el producto',
                        'Párrafo 3: 3 formas en que me ayuda diariamente',
                        'Párrafo 4: Lo que dice mi familia',
                        'Párrafo 5: Dónde conseguirlo con descuento'
                    ],
                    'elementos': 'Incluye 2-3 fotos reales, un video corto si es posible',
                    'cta': '👇 Les dejo el link en los comentarios (hay descuento esta semana)'
                },
                'success_rate': 73.9
            },
            {
                'name': 'Email Marketing B2B',
                'category': 'negocios',
                'platform': 'email',
                'template_content': {
                    'subject_lines': [
                        '{FirstName}, reduje mis costos 40% con esta herramienta',
                        'El secreto que usan el 73% de empresas exitosas',
                        'Quick question about your {pain_point}'
                    ],
                    'estructura': [
                        'Saludo personalizado',
                        'Pain point específico (1-2 líneas)',
                        'Solución con datos duros',
                        'Caso de éxito breve',
                        'CTA claro y único',
                        'P.D. con urgencia o beneficio extra'
                    ],
                    'cta': 'Reserva una demo de 15 minutos aquí →',
                    'tips': 'Mantén bajo 150 palabras, personaliza el primer párrafo'
                },
                'success_rate': 68.2
            }
        ]
        
        created_count = 0
        for template_data in templates:
            template, created = MarketingTemplate.objects.get_or_create(
                name=template_data['name'],
                platform=template_data['platform'],
                defaults=template_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Creada plantilla: {template.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Ya existe: {template.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✨ Total: {created_count} plantillas creadas')
        )