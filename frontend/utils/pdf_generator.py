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
    
    # === ENTITY NARRATIVE / COMPLETE STORY ===
    entity_narrative = report_data.get('entity_narrative', '')
    if entity_narrative:
        elements.append(Paragraph("THE COMPLETE STORY", heading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        narrative_intro = f"""
        <b>Who is {report_data.get('target_entity', 'this entity')}? What's the full story?</b><br/>
        This section provides a comprehensive narrative that ties together all the key facts, events, and timeline into a cohesive story.
        """
        elements.append(Paragraph(narrative_intro, body_style))
        elements.append(Spacer(1, 0.15*inch))
        
        # Split narrative into paragraphs
        paragraphs = entity_narrative.split('\n\n')
        for para in paragraphs:
            if para.strip():
                # Apply bold keywords to narrative
                para_text = _make_keywords_bold(para.strip())
                elements.append(Paragraph(para_text, body_style))
                elements.append(Spacer(1, 0.1*inch))
        
        elements.append(PageBreak())
    
    # === REPORT COMPONENTS OVERVIEW (Formatted with Headings & Bullets) ===
    elements.append(Paragraph("REPORT COMPONENTS OVERVIEW", heading_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # Component 1
    elements.append(Paragraph("<b>1. Biographical & Professional Details</b>", subheading_style))
    comp1_text = """
    Verified personal details, career trajectory, and professional history covering:
    • <b>Education</b> background and academic credentials
    • <b>Employment</b> history and career progression
    • <b>Professional</b> certifications and licenses
    • <b>Family</b> relationships and personal connections
    • <b>Biographical</b> information and background verification
    """
    elements.append(Paragraph(comp1_text, body_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Component 2
    elements.append(Paragraph("<b>2. Financial/Organizational Connections Map</b>", subheading_style))
    comp2_text = """
    A structured analysis of relationships between the target and other entities, covering:
    • <b>Financial</b> relationships (investments, funding, ownership stakes)
    • <b>Board</b> memberships and advisory positions
    • <b>Business</b> partnerships and professional associations
    • <b>Organizational</b> affiliations and institutional connections
    • <b>Investment</b> activities and portfolio companies
    """
    elements.append(Paragraph(comp2_text, body_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Component 3
    elements.append(Paragraph("<b>3. Identified Red Flags & Risk Factors</b>", subheading_style))
    comp3_text = """
    Comprehensive enumeration of potential risks and concerning patterns:
    • <b>Legal</b> issues (lawsuits, litigation, legal disputes)
    • <b>Regulatory</b> violations and compliance issues
    • <b>Financial</b> risks (fraud, bankruptcy, tax issues)
    • <b>Reputation</b> concerns and public controversies
    • <b>Conflicts of interest</b> and ethical concerns
    """
    elements.append(Paragraph(comp3_text, body_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Component 4
    elements.append(Paragraph("<b>4. Source Validation & Confidence Scoring</b>", subheading_style))
    comp4_text = """
    Every key finding includes source attribution and confidence assessment:
    • <b>Source URLs</b> for all information collected
    • <b>Confidence scores</b> (0-100%) based on source credibility
    • <b>Cross-reference</b> validation across multiple sources
    • <b>Verification</b> status for each fact
    """
    elements.append(Paragraph(comp4_text, body_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Component 5
    elements.append(Paragraph("<b>5. Strategic Insights & Summary</b>", subheading_style))
    comp5_text = """
    Final risk assessment and strategic recommendations:
    • <b>Overall risk level</b> (Critical, High, Medium, Low)
    • <b>Key findings</b> and material discoveries
    • <b>Recommendations</b> for decision-making
    • <b>Areas requiring</b> additional due diligence
    """
    elements.append(Paragraph(comp5_text, body_style))
    
    elements.append(PageBreak())
    
    # === SECTION 1: BIOGRAPHICAL & PROFESSIONAL DETAILS ===
    elements.append(Paragraph("1. BIOGRAPHICAL & PROFESSIONAL DETAILS", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    key_findings = report_data.get('key_findings', [])
    
    # Organize biographical facts by category
    bio_categories = {
        'education': [],
        'employment': [],
        'professional': [],
        'family': [],
        'personal': [],
        'biographical': []
    }
    
    for fact in key_findings:
        category = fact.get('category', '').lower()
        for key in bio_categories.keys():
            if key in category:
                bio_categories[key].append(fact)
                break
    
    # Display facts by category with bold category names
    category_names = {
        'education': '<b>EDUCATION & ACADEMIC BACKGROUND</b>',
        'employment': '<b>EMPLOYMENT HISTORY & CAREER</b>',
        'professional': '<b>PROFESSIONAL CREDENTIALS & EXPERIENCE</b>',
        'family': '<b>FAMILY & PERSONAL RELATIONSHIPS</b>',
        'personal': '<b>PERSONAL BACKGROUND</b>',
        'biographical': '<b>BIOGRAPHICAL INFORMATION</b>'
    }
    
    has_bio_data = False
    for category_key, category_label in category_names.items():
        facts = bio_categories[category_key]
        if facts:
            has_bio_data = True
            elements.append(Paragraph(category_label, subheading_style))
            elements.append(Spacer(1, 0.05*inch))
            
            for fact in facts[:10]:  # Limit per category
                confidence = fact.get('confidence', 0)
                content = fact.get('content', 'N/A')
                
                # Make key terms bold in content
                content = _make_keywords_bold(content)
                
                verified = '✓ Verified' if fact.get('verified', False) else '⚠ Unverified'
                sources = fact.get('sources', [])
                
                fact_text = f"• {content}<br/><i>  └ {verified} | Confidence: {confidence*100:.0f}%</i>"
                elements.append(Paragraph(fact_text, body_style))
                
                # Add source URL
                if sources:
                    source_url = sources[0] if isinstance(sources, list) else str(sources)
                    source_text = f'  <i><font color="blue">Source: {source_url[:80]}{"..." if len(source_url) > 80 else ""}</font></i>'
                    elements.append(Paragraph(source_text, ParagraphStyle('SourceText', parent=body_style, fontSize=8, leftIndent=15, spaceAfter=8)))
                
                elements.append(Spacer(1, 0.05*inch))
            
            elements.append(Spacer(1, 0.1*inch))
    
    if not has_bio_data:
        elements.append(Paragraph("No biographical information available.", body_style))
    
    elements.append(Spacer(1, 0.2*inch))
    elements.append(PageBreak())
    
    # === SECTION 2: FINANCIAL/ORGANIZATIONAL CONNECTIONS MAP ===
    elements.append(Paragraph("2. FINANCIAL/ORGANIZATIONAL CONNECTIONS MAP", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    intro_text = """
    This section maps all identified relationships between the target entity and other <b>individuals</b>, 
    <b>organizations</b>, <b>companies</b>, and <b>institutions</b>. Connections are categorized by relationship 
    type and assessed for strength based on available evidence.
    """
    elements.append(Paragraph(intro_text, body_style))
    elements.append(Spacer(1, 0.15*inch))
    
    connections = report_data.get('connection_network', [])
    
    if connections:
        # Group connections by relationship type
        conn_by_type = {}
        for conn in connections:
            rel_type = conn.get('relationship', 'other').lower()
            if rel_type not in conn_by_type:
                conn_by_type[rel_type] = []
            conn_by_type[rel_type].append(conn)
        
        # Relationship type labels with bold formatting
        type_labels = {
            'financial': '<b>FINANCIAL CONNECTIONS</b>',
            'business': '<b>BUSINESS RELATIONSHIPS</b>',
            'professional': '<b>PROFESSIONAL ASSOCIATIONS</b>',
            'family': '<b>FAMILY CONNECTIONS</b>',
            'political': '<b>POLITICAL AFFILIATIONS</b>',
            'board': '<b>BOARD & ADVISORY ROLES</b>',
            'investment': '<b>INVESTMENT RELATIONSHIPS</b>',
            'other': '<b>OTHER CONNECTIONS</b>'
        }
        
        for rel_type, label in type_labels.items():
            if rel_type in conn_by_type:
                elements.append(Paragraph(label, subheading_style))
                elements.append(Spacer(1, 0.05*inch))
                
                for conn in conn_by_type[rel_type][:15]:  # Limit per type
                    source = conn.get('source', 'N/A')
                    target = conn.get('target', 'N/A')
                    strength = conn.get('strength', 0) * 100
                    evidence = conn.get('evidence', [])
                    
                    # Determine strength indicator
                    if strength >= 80:
                        strength_indicator = "🔴 <b>Strong</b>"
                    elif strength >= 50:
                        strength_indicator = "🟡 <b>Medium</b>"
                    else:
                        strength_indicator = "🟢 <b>Weak</b>"
                    
                    conn_text = f"• <b>{target}</b> ({strength_indicator} - {strength:.0f}%)"
                    elements.append(Paragraph(conn_text, body_style))
                    
                    # Add evidence if available
                    if evidence:
                        evidence_text = evidence[0] if isinstance(evidence, list) else str(evidence)
                        # Escape HTML to avoid nested tag conflicts
                        evidence_text = evidence_text.replace('<', '&lt;').replace('>', '&gt;')
                        # Show more evidence text (up to 300 chars instead of 150)
                        truncated_evidence = evidence_text[:300] + ("..." if len(evidence_text) > 300 else "")
                        elements.append(Paragraph(f"  <i>└ {truncated_evidence}</i>", 
                                                ParagraphStyle('Evidence', parent=body_style, fontSize=8, leftIndent=15, spaceAfter=6)))
                    
                    elements.append(Spacer(1, 0.05*inch))
                
                elements.append(Spacer(1, 0.1*inch))
    else:
        elements.append(Paragraph("No connection data available at this time.", body_style))
    
    elements.append(Spacer(1, 0.2*inch))
    elements.append(PageBreak())
    
    # === SECTION 3: IDENTIFIED RED FLAGS & RISK FACTORS ===
    elements.append(Paragraph("3. IDENTIFIED RED FLAGS & RISK FACTORS", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    intro_text = """
    This section identifies potential <b>risks</b>, <b>inconsistencies</b>, <b>legal issues</b>, 
    <b>regulatory concerns</b>, and other <b>red flags</b> discovered during the investigation. 
    Risks are categorized by severity and supported by evidence.
    """
    elements.append(Paragraph(intro_text, body_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # Organize risks by severity category
    risk_categories = {
        'critical': risk_assessment.get('critical_risks', []),
        'high': risk_assessment.get('high_risks', []),
        'medium': risk_assessment.get('medium_risks', []),
        'low': risk_assessment.get('low_risks', [])
    }
    
    severity_labels = {
        'critical': ('<b>CRITICAL RISKS</b> 🔴', colors.HexColor('#ff0000')),
        'high': ('<b>HIGH PRIORITY RISKS</b> 🟠', colors.HexColor('#ff6600')),
        'medium': ('<b>MEDIUM PRIORITY RISKS</b> 🟡', colors.HexColor('#ffcc00')),
        'low': ('<b>LOW PRIORITY RISKS</b> 🟢', colors.HexColor('#00cc00'))
    }
    
    has_risks = False
    for severity, (label, color) in severity_labels.items():
        risks = risk_categories[severity]
        if risks:
            has_risks = True
            elements.append(Paragraph(label, subheading_style))
            elements.append(Spacer(1, 0.05*inch))
            
            for i, risk in enumerate(risks, 1):
                risk_type = risk.get('type', 'Unknown').replace('_', ' ').title()
                description = risk.get('description', 'No description available')
                description = _make_keywords_bold(description)
                confidence = risk.get('confidence', 0)
                impact = risk.get('impact', 'Unknown')
                evidence = risk.get('evidence', [])
                
                risk_text = f"""
                <b>{i}. {risk_type}</b><br/>
                {description}<br/>
                <i>└ Confidence: {confidence*100:.0f}% | Impact: {impact}</i>
                """
                elements.append(Paragraph(risk_text, body_style))
                
                # Add evidence/source if available
                if evidence:
                    evidence_text = evidence[0] if isinstance(evidence, list) else str(evidence)
                    # Don't apply bold to evidence text to avoid nested HTML tag conflicts
                    evidence_text = evidence_text.replace('<', '&lt;').replace('>', '&gt;')  # Escape any HTML
                    # Show more evidence text (up to 250 chars instead of 120)
                    truncated_evidence = evidence_text[:250] + ("..." if len(evidence_text) > 250 else "")
                    elements.append(Paragraph(f'  <i><font color="gray">Evidence: {truncated_evidence}</font></i>', 
                                            ParagraphStyle('EvidenceText', parent=body_style, fontSize=8, leftIndent=15, spaceAfter=8)))
                
                elements.append(Spacer(1, 0.08*inch))
            
            elements.append(Spacer(1, 0.15*inch))
    
    if not has_risks:
        elements.append(Paragraph("✓ No significant risks or red flags identified in the investigation.", body_style))
    
    elements.append(Spacer(1, 0.2*inch))
    elements.append(PageBreak())
    
    # === SECTION 4: SOURCE VALIDATION & CONFIDENCE SCORING ===
    elements.append(Paragraph("4. SOURCE VALIDATION & CONFIDENCE SCORING", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    intro_text = """
    All information in this report is attributed to <b>verified sources</b>. Each fact includes 
    a <b>confidence score</b> based on source <b>credibility</b>, <b>cross-reference validation</b>, 
    and <b>consistency</b> across multiple sources.
    """
    elements.append(Paragraph(intro_text, body_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # Confidence distribution
    high_conf = metadata.get('high_confidence_facts', 0)
    total_facts = metadata.get('total_facts_discovered', 0)
    avg_conf = metadata.get('average_confidence', 0)
    
    elements.append(Paragraph("<b>Overall Confidence Metrics:</b>", subheading_style))
    validation_text = f"""
    • <b>Average Confidence Score:</b> {avg_conf*100:.1f}%<br/>
    • <b>High Confidence Facts</b> (>80%): {high_conf} out of {total_facts}<br/>
    • <b>Total Facts Verified:</b> {metadata.get('total_verified_facts', 0)}<br/>
    • <b>Total Sources Consulted:</b> {len(_extract_unique_sources(key_findings))}<br/>
    """
    elements.append(Paragraph(validation_text, body_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # List all unique sources/websites
    elements.append(Paragraph("<b>Sources Consulted (Websites):</b>", subheading_style))
    elements.append(Spacer(1, 0.05*inch))
    
    unique_sources = _extract_unique_sources(key_findings)
    if unique_sources:
        for i, source_url in enumerate(unique_sources[:30], 1):  # Limit to 30 sources
            source_text = f'{i}. <font color="blue">{source_url}</font>'
            elements.append(Paragraph(source_text, ParagraphStyle('SourceList', parent=body_style, fontSize=8, leftIndent=10, spaceAfter=4)))
    else:
        elements.append(Paragraph("No source URLs available.", body_style))
    
    elements.append(Spacer(1, 0.2*inch))
    
    # Top verified facts with sources
    elements.append(Paragraph("<b>Top Verified Facts with Sources:</b>", subheading_style))
    elements.append(Spacer(1, 0.05*inch))
    
    verified_facts = [f for f in key_findings if f.get('verified', False)]
    if verified_facts:
        for i, fact in enumerate(verified_facts[:10], 1):
            content = fact.get('content', 'N/A')
            content = _make_keywords_bold(content)
            confidence = fact.get('confidence', 0)
            sources = fact.get('sources', [])
            
            fact_text = f"{i}. {content}<br/><i>  └ Confidence: {confidence*100:.0f}%</i>"
            elements.append(Paragraph(fact_text, body_style))
            
            if sources:
                source_url = sources[0] if isinstance(sources, list) else str(sources)
                source_text = f'  <i><font color="blue">Source: {source_url}</font></i>'
                elements.append(Paragraph(source_text, ParagraphStyle('SourceText', parent=body_style, fontSize=8, leftIndent=15, spaceAfter=8)))
            
            elements.append(Spacer(1, 0.05*inch))
    else:
        elements.append(Paragraph("No verified facts available.", body_style))
    
    elements.append(PageBreak())
    
    # === SECTION 5: STRATEGIC INSIGHTS & SUMMARY ===
    elements.append(Paragraph("5. STRATEGIC INSIGHTS & SUMMARY", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    intro_text = """
    This final section provides a comprehensive <b>risk profile</b> of the target entity and 
    <b>strategic recommendations</b> based on all findings from the investigation.
    """
    elements.append(Paragraph(intro_text, body_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # Risk profile summary
    elements.append(Paragraph("<b>RISK PROFILE SUMMARY</b>", subheading_style))
    risk_summary_text = f"""
    The target entity has been assessed with an <b>{overall_risk}</b> overall <b>risk level</b> 
    based on comprehensive analysis of <b>biographical</b> data, <b>financial</b> connections, 
    <b>legal</b> history, and <b>reputation</b> factors.
    """
    elements.append(Paragraph(risk_summary_text, body_style))
    elements.append(Spacer(1, 0.1*inch))
    
    elements.append(Paragraph("<b>KEY RISK INDICATORS</b>", subheading_style))
    risk_indicators = f"""
    • <b>Critical Risks</b> Identified: {len(risk_assessment.get('critical_risks', []))}<br/>
    • <b>High Priority Risks:</b> {len(risk_assessment.get('high_risks', []))}<br/>
    • <b>Medium Priority Risks:</b> {len(risk_assessment.get('medium_risks', []))}<br/>
    • <b>Low Priority Risks:</b> {len(risk_assessment.get('low_risks', []))}<br/>
    • <b>Total Connections</b> Mapped: {len(report_data.get('connection_network', []))}<br/>
    • <b>Average Confidence</b> Score: {avg_conf*100:.1f}%
    """
    elements.append(Paragraph(risk_indicators, body_style))
    elements.append(Spacer(1, 0.15*inch))
    
    elements.append(Paragraph("<b>RECOMMENDATION</b>", subheading_style))
    recommendation = _get_risk_recommendation(overall_risk)
    recommendation = _make_keywords_bold(recommendation)
    elements.append(Paragraph(recommendation, body_style))
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


def _make_keywords_bold(text: str) -> str:
    """
    Make important keywords bold in text for better readability
    """
    keywords = [
        # Professional & Career
        'employment', 'employed', 'career', 'job', 'position', 'role', 'work', 'worked',
        'education', 'degree', 'university', 'college', 'graduated', 'studied',
        'professional', 'certification', 'certified', 'license', 'licensed',
        'CEO', 'CFO', 'CTO', 'founder', 'co-founder', 'director', 'manager', 'executive',
        
        # Financial
        'financial', 'finance', 'investment', 'invested', 'investor', 'funding', 'funded',
        'revenue', 'profit', 'loss', 'income', 'assets', 'capital', 'equity', 'stock',
        'board', 'board member', 'shareholder', 'ownership', 'owns', 'acquired',
        'bankruptcy', 'bankrupt', 'insolvent', 'debt', 'creditor',
        
        # Legal & Risk
        'lawsuit', 'sued', 'litigation', 'legal', 'court', 'trial', 'settlement',
        'fraud', 'fraudulent', 'criminal', 'investigation', 'investigated', 'SEC',
        'regulatory', 'regulation', 'compliance', 'violation', 'violated', 'penalty',
        'sanctions', 'sanctioned', 'indictment', 'indicted', 'convicted', 'guilty',
        'misconduct', 'allegation', 'alleged', 'accused',
        
        # Relationships
        'family', 'spouse', 'married', 'partner', 'relative', 'sibling', 'parent',
        'business', 'company', 'organization', 'firm', 'corporation', 'enterprise',
        'political', 'politics', 'politician', 'government', 'campaign', 'donation',
        'association', 'affiliated', 'connected', 'relationship', 'partnership',
        
        # Reputation & Risk Indicators
        'scandal', 'controversy', 'controversial', 'conflict of interest',
        'suspicious', 'questionable', 'concerns', 'risk', 'red flag',
        'resignation', 'resigned', 'terminated', 'fired', 'dismissed'
    ]
    
    # Sort by length (longest first) to avoid partial replacements
    keywords.sort(key=len, reverse=True)
    
    result = text
    for keyword in keywords:
        # Case-insensitive replacement with word boundaries
        import re
        pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
        result = pattern.sub(lambda m: f'<b>{m.group(0)}</b>', result)
    
    return result


def _extract_unique_sources(facts: list) -> list:
    """
    Extract unique source URLs from all facts
    """
    unique_urls = set()
    
    for fact in facts:
        sources = fact.get('sources', [])
        if isinstance(sources, list):
            for source in sources:
                if isinstance(source, str) and (source.startswith('http://') or source.startswith('https://')):
                    unique_urls.add(source)
        elif isinstance(sources, str) and (sources.startswith('http://') or sources.startswith('https://')):
            unique_urls.add(sources)
    
    return sorted(list(unique_urls))


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

