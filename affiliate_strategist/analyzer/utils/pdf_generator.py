# REEMPLAZAR tu pdf_generator.py con esta versión mejorada

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.colors import HexColor
import io
from datetime import datetime
import re

def clean_text_for_pdf(text):
    """Limpia el texto para evitar errores de parsing en ReportLab"""
    if not text:
        return ""
    
    # Eliminar markdown
    text = re.sub(r'#{1,6}\s*', '', text)  # Eliminar headers ###
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)  # Convertir **texto** a <b>texto</b>
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)  # Convertir *texto* a <i>texto</i>
    
    # Limpiar tags HTML mal formateados
    text = re.sub(r'<b>\s*</b>', '', text)  # Eliminar tags vacíos
    text = re.sub(r'<i>\s*</i>', '', text)
    
    # Asegurar que los tags estén balanceados
    b_open = text.count('<b>')
    b_close = text.count('</b>')
    if b_open > b_close:
        text += '</b>' * (b_open - b_close)
    elif b_close > b_open:
        text = '<b>' * (b_close - b_open) + text
        
    # Convertir saltos de línea
    text = text.replace('\n\n', '<br/><br/>')
    text = text.replace('\n', '<br/>')
    
    # Convertir listas
    text = re.sub(r'^[-•]\s*(.+)$', r'• \1', text, flags=re.MULTILINE)
    
    # Escapar caracteres especiales para XML
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    
    # Restaurar tags HTML permitidos
    text = text.replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
    text = text.replace('&lt;i&gt;', '<i>').replace('&lt;/i&gt;', '</i>')
    text = text.replace('&lt;br/&gt;', '<br/>')
    
    return text

def detect_analysis_type(analysis):
    """Detecta si es análisis básico o competitivo"""
    # Verificar si tiene datos de competidores
    has_competitor_analysis = (
        hasattr(analysis, 'competitor_analysis') and 
        analysis.competitor_analysis and 
        analysis.competitor_analysis != {}
    )
    
    has_competitors = False
    if hasattr(analysis, 'competitoranalysis_set'):
        has_competitors = analysis.competitoranalysis_set.exists()
    
    # Verificar contenido de la respuesta
    competitive_keywords = [
        'competidor', 'competencia', 'rival', 'vs', 'comparación',
        'market share', 'posicionamiento', 'gap', 'ventaja competitiva'
    ]
    
    response_text = analysis.ai_response.lower() if analysis.ai_response else ""
    has_competitive_content = any(keyword in response_text for keyword in competitive_keywords)
    
    return has_competitor_analysis or has_competitors or has_competitive_content

def generate_basic_pdf(analysis, buffer):
    """Genera PDF para análisis básico"""
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=HexColor('#667eea'),
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#495057'),
        spaceAfter=15
    )
    
    # Título principal
    story.append(Paragraph("📊 Estrategia de Marketing de Afiliados", title_style))
    story.append(Spacer(1, 20))
    
    # Información del producto
    info_data = [
        ['Producto:', clean_text_for_pdf(analysis.product_title or 'Sin título')],
        ['Precio:', analysis.product_price or 'No disponible'],
        ['Plataforma:', analysis.get_platform_display()],
        ['Fecha:', analysis.created_at.strftime('%d/%m/%Y %H:%M')],
        ['Tipo:', 'Análisis Básico']
    ]
    
    info_table = Table(info_data, colWidths=[100, 300])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#495057')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#dee2e6')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 30))
    
    # Audiencia objetivo
    story.append(Paragraph("🎯 Audiencia Objetivo", subtitle_style))
    audience_text = clean_text_for_pdf(analysis.target_audience)
    story.append(Paragraph(audience_text, styles['Normal']))
    story.append(Spacer(1, 30))
    
    # Estrategia generada
    story.append(Paragraph("🚀 Estrategia Generada", subtitle_style))
    story.append(Spacer(1, 15))
    
    return story, doc

def generate_competitive_pdf(analysis, buffer):
    """Genera PDF para análisis competitivo"""
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=HexColor('#dc3545'),  # Rojo para competitivo
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#495057'),
        spaceAfter=15
    )
    
    # Título principal competitivo
    story.append(Paragraph("🥊 Análisis Competitivo Inteligente", title_style))
    story.append(Spacer(1, 20))
    
    # Información del análisis competitivo
    competitors_count = 0
    if hasattr(analysis, 'competitoranalysis_set'):
        competitors_count = analysis.competitoranalysis_set.count()
    
    info_data = [
        ['Producto Principal:', clean_text_for_pdf(analysis.product_title or 'Sin título')],
        ['Precio:', analysis.product_price or 'No disponible'],
        ['Plataforma:', analysis.get_platform_display()],
        ['Competidores Analizados:', str(competitors_count) if competitors_count > 0 else 'Múltiples'],
        ['Fecha:', analysis.created_at.strftime('%d/%m/%Y %H:%M')],
        ['Tipo:', 'Análisis Competitivo Completo']
    ]
    
    info_table = Table(info_data, colWidths=[120, 280])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#fff5f5')),  # Fondo rojizo suave
        ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#dc3545')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#f8d7da')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 30))
    
    # Análisis de precios (si existe)
    if hasattr(analysis, 'competitor_analysis') and analysis.competitor_analysis:
        story.append(Paragraph("💰 Análisis de Precios Competitivos", subtitle_style))
        
        pricing_info = analysis.competitor_analysis
        position = pricing_info.get('position', 'unknown')
        recommendation = pricing_info.get('recommendation', 'No disponible')
        
        position_text = {
            'premium': '🔥 PREMIUM - Producto de alta gama',
            'competitive': '⚖️ COMPETITIVO - En rango del mercado',
            'cheapest': '💰 ECONÓMICO - Precio más bajo',
            'unknown': '❓ Posición indeterminada'
        }.get(position, 'Sin determinar')
        
        pricing_data = [
            ['Tu Posición:', position_text],
            ['Recomendación:', recommendation]
        ]
        
        pricing_table = Table(pricing_data, colWidths=[100, 300])
        pricing_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#fff3cd')),
            ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#856404')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#ffeaa7')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(pricing_table)
        story.append(Spacer(1, 20))
    
    # Lista de competidores
    if hasattr(analysis, 'competitoranalysis_set') and analysis.competitoranalysis_set.exists():
        story.append(Paragraph("🏆 Competidores Analizados", subtitle_style))
        
        competitors = analysis.competitoranalysis_set.all()
        for i, competitor in enumerate(competitors, 1):
            comp_text = f"<b>Competidor {i}:</b> {competitor.competitor_name}<br/>"
            comp_text += f"<i>URL:</i> {competitor.competitor_url}<br/>"
            story.append(Paragraph(comp_text, styles['Normal']))
            story.append(Spacer(1, 10))
    
    story.append(Spacer(1, 20))
    
    # Audiencia objetivo
    story.append(Paragraph("🎯 Audiencia Objetivo", subtitle_style))
    audience_text = clean_text_for_pdf(analysis.target_audience)
    story.append(Paragraph(audience_text, styles['Normal']))
    story.append(Spacer(1, 30))
    
    # Estrategia competitiva generada
    story.append(Paragraph("⚔️ Estrategia Competitiva", subtitle_style))
    story.append(Spacer(1, 15))
    
    return story, doc

def generate_strategy_pdf(analysis):
    """Genera PDF adaptado al tipo de análisis"""
    try:
        # Detectar tipo de análisis
        is_competitive = detect_analysis_type(analysis)
        
        # Buffer en memoria
        buffer = io.BytesIO()
        
        # Generar PDF según el tipo
        if is_competitive:
            story, doc = generate_competitive_pdf(analysis, buffer)
        else:
            story, doc = generate_basic_pdf(analysis, buffer)
        
        # Procesar el contenido de la estrategia
        strategy_content = clean_text_for_pdf(analysis.ai_response)
        
        # Dividir por párrafos y procesar cada uno
        paragraphs = strategy_content.split('<br/><br/>')
        
        for para in paragraphs:
            if para.strip():
                try:
                    # Intentar crear el párrafo
                    p = Paragraph(para.strip(), getSampleStyleSheet()['Normal'])
                    story.append(p)
                    story.append(Spacer(1, 12))
                except Exception as e:
                    # Si falla, agregar como texto plano
                    clean_para = re.sub(r'<[^>]+>', '', para)  # Eliminar todos los tags
                    story.append(Paragraph(clean_para.strip(), getSampleStyleSheet()['Normal']))
                    story.append(Spacer(1, 12))
        
        # Footer
        story.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            'Footer',
            parent=getSampleStyleSheet()['Normal'],
            fontSize=10,
            textColor=HexColor('#666666'),
            alignment=TA_CENTER
        )
        
        analysis_type = "Competitivo" if is_competitive else "Básico"
        footer_text = f"Affiliate Strategist - Análisis {analysis_type} - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        story.append(Paragraph(footer_text, footer_style))
        
        # Construir PDF
        doc.build(story)
        
        # Obtener el valor del buffer
        pdf = buffer.getvalue()
        buffer.close()
        
        return pdf
        
    except Exception as e:
        print(f"Error en generate_strategy_pdf: {str(e)}")
        # En caso de error, generar un PDF simple
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        story.append(Paragraph("Estrategia de Marketing", styles['Title']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Producto: {analysis.product_title}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Texto plano sin formato
        clean_response = re.sub(r'[#*_`~]', '', analysis.ai_response)
        story.append(Paragraph("Estrategia:", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Dividir en líneas cortas para evitar problemas
        lines = clean_response.split('\n')
        for line in lines:
            if line.strip():
                try:
                    story.append(Paragraph(line.strip()[:200], styles['Normal']))
                    story.append(Spacer(1, 6))
                except:
                    pass
        
        doc.build(story)
        pdf = buffer.getvalue()
        buffer.close()
        
        return pdf