import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf_report(audit_result: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor("#1A202C"),
        spaceAfter=12
    )
    
    story.append(Paragraph("Network Configuration Compliance Audit Report", title_style))
    story.append(Spacer(1, 10))

    # Executive Summary Table
    meta = audit_result.get("extracted_metadata", {})
    summary_data = [
        [Paragraph("<b>Target Hostname:</b>", styles['Normal']), Paragraph(audit_result.get("hostname", "N/A"), styles['Normal']),
         Paragraph("<b>Compliance Status:</b>", styles['Normal']), Paragraph(f"<b>{audit_result.get('status')}</b>", styles['Normal'])],
        [Paragraph("<b>Vendor:</b>", styles['Normal']), Paragraph(meta.get("vendor", "N/A").upper(), styles['Normal']),
         Paragraph("<b>Violation Count:</b>", styles['Normal']), Paragraph(str(audit_result.get("violation_count", 0)), styles['Normal'])]
    ]
    
    summary_table = Table(summary_data, colWidths=[120, 150, 120, 150])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F7FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))

    # Violations Findings Table
    story.append(Paragraph("Detailed Compliance Findings & Remediation", styles['Heading2']))
    story.append(Spacer(1, 8))

    violations = audit_result.get("violations", [])
    if not violations:
        story.append(Paragraph("No security violations detected. Device meets target compliance benchmarks.", styles['Normal']))
    else:
        table_data = [["Rule ID", "Severity", "Finding Title", "Remediation Path"]]
        for v in violations:
            table_data.append([
                v.get("rule_id", "N/A"),
                v.get("severity", "N/A"),
                Paragraph(v.get("title", ""), styles['Normal']),
                Paragraph(v.get("remediation", ""), styles['Normal'])
            ])

        findings_table = Table(table_data, colWidths=[70, 65, 160, 245])
        findings_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2B6CB0")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(findings_table)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()