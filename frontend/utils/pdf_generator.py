"""
PDF Report Generator for Deep Research Agent
Generates comprehensive due diligence reports in PDF format
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, 
    Spacer, PageBreak, Image, Frame, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from datetime import datetime
import io


def generate_pdf_report(report_data: dict) -> bytes:
    """
    Generate a comprehensive PDF report from research data
    
    Args:
        report_data: Dictionary containing research results
    
    Returns:
        bytes: PDF file as bytes
    """
    buffer = io.BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Container for PDF elements
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2e86ab'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#555555'),
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=12
    )
    
    # === PAGE 1: TITLE PAGE ===
    elements.append(Spacer(1, 1.5*inch))
    
    # Title
    title = Paragraph("DUE DILIGENCE RESEARCH REPORT", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.3*inch))
    
    # Target entity
    target_style = ParagraphStyle('Target', parent=styles['Normal'], fontSize=14, alignment=TA_CENTER)
    elements.append(Paragraph(f"<b>Target:</b> {report_data.get('target_entity', 'N/A')}", target_style))
    elements.append(Spacer(1, 0.5*inch))
    
    # Report metadata
    metadata = report_data.get('research_metadata', {})
    report_info = [
        ['Report Date:', datetime.now().strftime('%B %d, %Y')],
        ['Report ID:', report_data.get('session_id', 'N/A')[:16]],
        ['Research Depth:', str(metadata.get('research_depth', 'N/A'))],
        ['Total Facts Verified:', str(metadata.get('total_verified_facts', 'N/A'))],
        ['Average Confidence:', f"{metadata.get('average_confidence', 0)*100:.1f}%"],
    ]
    
    info_table = Table(report_info, colWidths=[2*inch, 3*inch])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
        ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Confidentiality notice
    conf_text = """
    <b>CONFIDENTIAL</b><br/>
    This report contains confidential information intended solely for the use of the recipient. 
    Unauthorized distribution or copying is strictly prohibited.
    """
    elements.append(Paragraph(conf_text, ParagraphStyle('Conf', parent=body_style, fontSize=9, alignment=TA_CENTER)))
    
    elements.append(PageBreak())
    
    # === PAGE 2: EXECUTIVE SUMMARY ===
    elements.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    executive_summary = report_data.get('executive_summary', 'No executive summary available.')
    elements.append(Paragraph(executive_summary, body_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Overall Risk Assessment
    risk_assessment = report_data.get('risk_assessment', {})
    overall_risk = risk_assessment.get('overall_risk_level', 'unknown').upper()
    
    risk_colors_map = {
        'CRITICAL': colors.HexColor('#ff4444'),
        'HIGH': colors.HexColor('#ff8800'),
        'MEDIUM': colors.HexColor('#ffcc00'),
        'LOW': colors.HexColor('#00cc00'),
        'UNKNOWN': colors.HexColor('#999999')
    }
    
    risk_color = risk_colors_map.get(overall_risk, risk_colors_map['UNKNOWN'])
    
    risk_data = [[f"OVERALL RISK LEVEL: {overall_risk}"]]
    risk_table = Table(risk_data, colWidths=[6.5*inch])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), risk_color),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONT', (0, 0), (-1, -1), 'Helvetica-Bold', 14),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BOX', (0, 0), (-1, -1), 2, colors.white)
    ]))
    
    elements.append(risk_table)
    elements.append(Spacer(1, 0.3*inch))
    
    elements.append(PageBreak())
    
    # === COMPONENT TABLE (User's Requested Format) ===
    elements.append(Paragraph("REPORT COMPONENTS OVERVIEW", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    components_data = [
        ['Component', 'Description', 'Functional Requirement Addressed'],
        [
            'Biographical & Professional Details',
            'Verified personal details, career trajectory, and professional history.',
            'Deep Fact Extraction'
        ],
        [
            'Financial/Organizational Connections Map',
            'A structured map of relationships between the target and other entities, organizations, or individuals (e.g., board seats, investments, shared contacts).',
            'Connection Mapping'
        ],
        [
            'Identified Red Flags',
            'Clear enumeration of potential risks, inconsistencies, concerning associations, or behavioral patterns found (e.g., lawsuits, regulatory issues, conflicts of interest).',
            'Risk Pattern Recognition'
        ],
        [
            'Source Validation & Confidence Scoring',
            'For every key finding, a reference to the source and an associated confidence score (e.g., "High confidence: 95%" for information cross-referenced across three verified sources).',
            'Source Validation'
        ],
        [
            'Strategic Insights & Summary',
            'A final summary of the target\'s overall risk profile (e.g., Low, Medium, High Risk) and strategic insights relevant to due diligence.',
            'Quality of Risk Assessment Insights'
        ]
    ]
    
    comp_table = Table(components_data, colWidths=[1.8*inch, 3*inch, 1.7*inch])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
        ('FONT', (0, 1), (-1, -1), 'Helvetica', 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
    ]))
    
    elements.append(comp_table)
    elements.append(PageBreak())
    
    # === SECTION 1: BIOGRAPHICAL & PROFESSIONAL DETAILS ===
    elements.append(Paragraph("1. BIOGRAPHICAL & PROFESSIONAL DETAILS", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    key_findings = report_data.get('key_findings', [])
    
    # Filter biographical facts
    bio_facts = [f for f in key_findings if f.get('category', '').lower() in ['biographical', 'professional', 'personal', 'employment']]
    
    if bio_facts:
        for fact in bio_facts[:15]:  # Limit to top 15
            confidence = fact.get('confidence', 0)
            content = fact.get('content', 'N/A')
            verified = '✓ Verified' if fact.get('verified', False) else '⚠ Unverified'
            
            fact_text = f"• {content} <i>({verified}, Confidence: {confidence*100:.0f}%)</i>"
            elements.append(Paragraph(fact_text, body_style))
    else:
        elements.append(Paragraph("No biographical information available.", body_style))
    
    elements.append(Spacer(1, 0.2*inch))
    elements.append(PageBreak())
    
    # === SECTION 2: FINANCIAL/ORGANIZATIONAL CONNECTIONS MAP ===
    elements.append(Paragraph("2. FINANCIAL/ORGANIZATIONAL CONNECTIONS MAP", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    connections = report_data.get('connection_network', [])
    
    if connections:
        conn_data = [['Source', 'Relationship', 'Target', 'Strength']]
        
        for conn in connections[:20]:  # Limit to top 20
            conn_data.append([
                str(conn.get('source', 'N/A'))[:30],
                str(conn.get('relationship', 'N/A'))[:20],
                str(conn.get('target', 'N/A'))[:30],
                f"{conn.get('strength', 0)*100:.0f}%"
            ])
        
        conn_table = Table(conn_data, colWidths=[2*inch, 1.5*inch, 2*inch, 1*inch])
        conn_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e86ab')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
        ]))
        
        elements.append(conn_table)
    else:
        elements.append(Paragraph("No connection data available.", body_style))
    
    elements.append(Spacer(1, 0.2*inch))
    elements.append(PageBreak())
    
    # === SECTION 3: IDENTIFIED RED FLAGS ===
    elements.append(Paragraph("3. IDENTIFIED RED FLAGS & RISK FACTORS", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Aggregate all risks
    all_risks = []
    all_risks.extend(risk_assessment.get('critical_risks', []))
    all_risks.extend(risk_assessment.get('high_risks', []))
    all_risks.extend(risk_assessment.get('medium_risks', []))
    all_risks.extend(risk_assessment.get('low_risks', []))
    
    if all_risks:
        for i, risk in enumerate(all_risks, 1):
            severity = risk.get('severity', 'unknown').upper()
            risk_type = risk.get('type', 'Unknown').replace('_', ' ').title()
            description = risk.get('description', 'No description available')
            confidence = risk.get('confidence', 0)
            impact = risk.get('impact', 'Unknown')
            
            risk_text = f"""
            <b>{i}. [{severity}] {risk_type}</b><br/>
            {description}<br/>
            <i>Confidence: {confidence*100:.0f}% | Impact: {impact}</i>
            """
            elements.append(Paragraph(risk_text, body_style))
            elements.append(Spacer(1, 0.1*inch))
    else:
        elements.append(Paragraph("No significant risks identified.", body_style))
    
    elements.append(Spacer(1, 0.2*inch))
    elements.append(PageBreak())
    
    # === SECTION 4: SOURCE VALIDATION & CONFIDENCE SCORING ===
    elements.append(Paragraph("4. SOURCE VALIDATION & CONFIDENCE SCORING", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Confidence distribution
    high_conf = metadata.get('high_confidence_facts', 0)
    total_facts = metadata.get('total_facts_discovered', 0)
    avg_conf = metadata.get('average_confidence', 0)
    
    validation_text = f"""
    <b>Overall Confidence Metrics:</b><br/>
    • Average Confidence Score: {avg_conf*100:.1f}%<br/>
    • High Confidence Facts (>80%): {high_conf} out of {total_facts}<br/>
    • Total Facts Verified: {metadata.get('total_verified_facts', 0)}<br/>
    • Total Sources Consulted: {metadata.get('sources_consulted', 0)}<br/>
    """
    elements.append(Paragraph(validation_text, body_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Top verified facts with sources
    elements.append(Paragraph("<b>Top Verified Facts with Sources:</b>", subheading_style))
    
    verified_facts = [f for f in key_findings if f.get('verified', False)]
    for fact in verified_facts[:10]:
        content = fact.get('content', 'N/A')
        confidence = fact.get('confidence', 0)
        sources = fact.get('sources', [])
        
        fact_text = f"• {content} <i>(Confidence: {confidence*100:.0f}%)</i>"
        elements.append(Paragraph(fact_text, body_style))
        
        if sources:
            source_text = f"  <i>Source: {sources[0][:100]}...</i>"
            elements.append(Paragraph(source_text, ParagraphStyle('SourceText', parent=body_style, fontSize=8, leftIndent=20)))
    
    elements.append(PageBreak())
    
    # === SECTION 5: STRATEGIC INSIGHTS & SUMMARY ===
    elements.append(Paragraph("5. STRATEGIC INSIGHTS & SUMMARY", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Risk profile summary
    risk_summary = f"""
    <b>Risk Profile Summary:</b><br/>
    The target has been assessed with an <b>{overall_risk}</b> overall risk level based on comprehensive analysis.<br/><br/>
    
    <b>Key Risk Indicators:</b><br/>
    • Critical Risks Identified: {len(risk_assessment.get('critical_risks', []))}<br/>
    • High Priority Risks: {len(risk_assessment.get('high_risks', []))}<br/>
    • Medium Priority Risks: {len(risk_assessment.get('medium_risks', []))}<br/>
    • Low Priority Risks: {len(risk_assessment.get('low_risks', []))}<br/><br/>
    
    <b>Recommendation:</b><br/>
    {_get_risk_recommendation(overall_risk)}
    """
    
    elements.append(Paragraph(risk_summary, body_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # === FOOTER ===
    footer_text = f"""
    <i>Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>
    Deep Research AI Agent - Comprehensive Due Diligence Platform<br/>
    Report ID: {report_data.get('session_id', 'N/A')}</i>
    """
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=body_style, fontSize=8, alignment=TA_CENTER)))
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes


def _get_risk_recommendation(risk_level: str) -> str:
    """Get recommendation based on risk level"""
    recommendations = {
        'CRITICAL': 'Immediate attention required. Recommend thorough investigation before proceeding. High risk of material impact on transaction or relationship.',
        'HIGH': 'Significant concerns identified. Recommend additional due diligence and risk mitigation strategies before proceeding.',
        'MEDIUM': 'Moderate risk factors present. Recommend monitoring and verification of key findings. Proceed with caution.',
        'LOW': 'No significant red flags identified. Standard monitoring and verification procedures recommended.',
        'UNKNOWN': 'Insufficient data for comprehensive risk assessment. Additional research recommended.'
    }
    
    return recommendations.get(risk_level.upper(), recommendations['UNKNOWN'])

