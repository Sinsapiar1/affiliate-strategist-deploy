# analyzer/utils/pdf_generator.py - GENERADOR PDF FUNCIONAL

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib import colors
import io
from datetime import datetime
import re

def clean_text_for_pdf(text):
    """Limpia texto para PDF evitando errores de parsing"""
    if not text:
        return ""
    
    # Limpiar markdown básico
    text = re.sub(r'#{1,6}\s*', '', text)  # Headers
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)  # Bold
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)  # Italic
    
    # Convertir saltos de línea
    text = text.replace('\n\n', '<br/><br/>')
    text = text.replace('\n', '<br/>')
    
    # Limpiar caracteres problemáticos
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    
    # Restaurar tags permitidos
    text = text.replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
    text = text.replace('&lt;i&gt;', '<i>').replace('&lt;/i&gt;', '</i>')
    text = text.replace('&lt;br/&gt;', '<br/>')
    
    return text

def generate_strategy_pdf(analysis):
    """Genera PDF de estrategia según el tipo de análisis"""
    try:
        buffer = io.BytesIO()
        
        # Detectar tipo de análisis
        is_competitive = (
            hasattr(analysis, 'analysis_type') and 
            analysis.analysis_type == 'competitive'
        ) or (
            analysis.ai_response and 
            any(keyword in analysis.ai_response.lower() for keyword in ['competidor', 'competencia', 'rival'])
        )
        
        # Configuración del documento
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # ✅ ESTILOS PERSONALIZADOS
        if is_competitive:
            primary_color = HexColor('#dc3545')  # Rojo para competitivo
            bg_color = HexColor('#fff5f5')
            title_text = "🥊 ANÁLISIS COMPETITIVO"
            subtitle_color = HexColor('#721c24')
        else:
            primary_color = HexColor('#667eea')  # Azul para básico
            bg_color = HexColor('#f8f9fa')
            title_text = "📊 ESTRATEGIA DE MARKETING"
            subtitle_color = HexColor('#495057')
        
        # Estilo de título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=20,
            textColor=primary_color,
            alignment=TA_CENTER,
            spaceAfter=30,
            fontName='Helvetica-Bold'
        )
        
        # Estilo de subtítulo
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=subtitle_color,
            spaceAfter=15,
            fontName='Helvetica-Bold'
        )
        
        # ✅ TÍTULO PRINCIPAL
        story.append(Paragraph(title_text, title_style))
        story.append(Spacer(1, 20))
        
        # ✅ INFORMACIÓN DEL PRODUCTO
        product_info = [
            ['Producto:', clean_text_for_pdf(analysis.product_title or 'Sin título')],
            ['Precio:', analysis.product_price or 'No disponible'],
            ['Plataforma:', analysis.get_platform_display() if hasattr(analysis, 'get_platform_display') else analysis.platform.title()],
            ['Tipo de Análisis:', 'Competitivo' if is_competitive else 'Básico'],
            ['Fecha:', analysis.created_at.strftime('%d/%m/%Y %H:%M') if hasattr(analysis, 'created_at') else datetime.now().strftime('%d/%m/%Y %H:%M')],
        ]
        
        info_table = Table(product_info, colWidths=[120, 350])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), bg_color),
            ('TEXTCOLOR', (0, 0), (0, -1), primary_color),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#dee2e6')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 30))
        
        # ✅ AUDIENCIA OBJETIVO
        if hasattr(analysis, 'target_audience') and analysis.target_audience:
            story.append(Paragraph("🎯 Audiencia Objetivo", subtitle_style))
            audience_text = clean_text_for_pdf(analysis.target_audience)
            story.append(Paragraph(audience_text, styles['Normal']))
            story.append(Spacer(1, 20))
        
        # ✅ ESTRATEGIA GENERADA
        strategy_title = "⚔️ Estrategia Competitiva" if is_competitive else "🚀 Estrategia de Marketing"
        story.append(Paragraph(strategy_title, subtitle_style))
        story.append(Spacer(1, 15))
        
        # ✅ PROCESAR CONTENIDO DE LA ESTRATEGIA
        if analysis.ai_response:
            strategy_content = clean_text_for_pdf(analysis.ai_response)
            
            # Dividir en párrafos más pequeños para evitar errores
            paragraphs = strategy_content.split('<br/><br/>')
            
            for i, para in enumerate(paragraphs):
                if para.strip():
                    try:
                        # Intentar crear párrafo normal
                        p = Paragraph(para.strip(), styles['Normal'])
                        story.append(p)
                        story.append(Spacer(1, 12))
                    except Exception as e:
                        # Si falla, crear párrafo sin formato
                        clean_para = re.sub(r'<[^>]+>', '', para)  # Remover tags
                        clean_para = clean_para.replace('&amp;', '&')
                        try:
                            p = Paragraph(clean_para.strip(), styles['Normal'])
                            story.append(p)
                            story.append(Spacer(1, 12))
                        except:
                            # Último recurso: texto plano muy simple
                            simple_text = clean_para[:500] + "..." if len(clean_para) > 500 else clean_para
                            try:
                                story.append(Paragraph(simple_text, styles['Normal']))
                                story.append(Spacer(1, 12))
                            except:
                                continue  # Saltar este párrafo si no se puede procesar
        
        # ✅ FOOTER
        story.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            textColor=HexColor('#666666'),
            alignment=TA_CENTER
        )
        
        analysis_type_text = "Competitivo" if is_competitive else "Básico"
        footer_text = f"Affiliate Strategist Pro - Análisis {analysis_type_text} - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        story.append(Paragraph(footer_text, footer_style))
        
        # ✅ CONSTRUIR PDF
        doc.build(story)
        
        # Obtener contenido del buffer
        pdf_value = buffer.getvalue()
        buffer.close()
        
        return pdf_value
        
    except Exception as e:
        print(f"Error en generate_strategy_pdf: {str(e)}")
        
        # ✅ FALLBACK: PDF SIMPLE EN CASO DE ERROR
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Título simple
        story.append(Paragraph("Estrategia de Marketing", styles['Title']))
        story.append(Spacer(1, 20))
        
        # Información básica
        story.append(Paragraph(f"Producto: {getattr(analysis, 'product_title', 'N/A')}", styles['Normal']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Plataforma: {getattr(analysis, 'platform', 'N/A')}", styles['Normal']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Estrategia (texto plano)
        if hasattr(analysis, 'ai_response') and analysis.ai_response:
            story.append(Paragraph("Estrategia:", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            # Dividir en líneas y agregar como párrafos simples
            lines = analysis.ai_response.split('\n')
            for line in lines[:20]:  # Máximo 20 líneas para evitar errores
                clean_line = re.sub(r'[#*_`~\[\]]', '', line.strip())
                if clean_line and len(clean_line) > 2:
                    try:
                        story.append(Paragraph(clean_line[:200], styles['Normal']))  # Máximo 200 chars por línea
                        story.append(Spacer(1, 6))
                    except:
                        continue
        
        # Footer simple
        story.append(Spacer(1, 30))
        story.append(Paragraph(f"Generado por Affiliate Strategist Pro - {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
        
        doc.build(story)
        pdf_value = buffer.getvalue()
        buffer.close()
        
        return pdf_value