"""
PDF Quote Generator for Novellus Loan Management System
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import tempfile
from datetime import datetime

def generate_quote_pdf(quote_data, application_data=None):
    """Generate PDF quote document"""
    # Create temporary file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        tmp_path = tmp_file.name
    
    # Create PDF document
    doc = SimpleDocTemplate(tmp_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph("Novellus Finance - Loan Quote", title_style))
    story.append(Spacer(1, 12))
    
    # Quote details table
    quote_details = [
        ['Quote ID:', str(quote_data.get('id', 'N/A'))],
        ['Date:', datetime.now().strftime('%d/%m/%Y')],
        ['Gross Amount:', f"£{quote_data.get('gross_amount', 0):,.2f}"],
        ['Net Advance:', f"£{quote_data.get('net_advance', 0):,.2f}"],
        ['Interest Rate:', f"{quote_data.get('interest_rate', 0):.2f}%"],
        ['Loan Term:', f"{quote_data.get('loan_term', 0)} months"],
        ['Monthly Payment:', f"£{quote_data.get('monthly_payment', 0):,.2f}"],
        ['Total Interest:', f"£{quote_data.get('total_interest', 0):,.2f}"],
    ]
    
    table = Table(quote_details, colWidths=[2*inch, 3*inch])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 24))
    
    # Footer
    footer_text = "This quote is subject to credit approval and full underwriting. Terms and conditions apply."
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER
    )
    story.append(Paragraph(footer_text, footer_style))
    
    # Build PDF
    doc.build(story)
    
    # Read the PDF content
    with open(tmp_path, 'rb') as f:
        pdf_content = f.read()
    
    # Clean up temporary file
    os.unlink(tmp_path)
    
    return pdf_content

def generate_professional_quote_docx(quote_data, application_data=None):
    """Generate professional DOCX quote document"""
    from docx import Document
    from docx.shared import Inches
    
    doc = Document()
    
    # Add title
    title = doc.add_heading('Novellus Finance - Loan Quote', 0)
    title.alignment = 1  # Center alignment
    
    # Add quote details
    doc.add_heading('Quote Details', level=1)
    
    table = doc.add_table(rows=8, cols=2)
    table.style = 'Table Grid'
    
    details = [
        ('Quote ID:', str(quote_data.get('id', 'N/A'))),
        ('Date:', datetime.now().strftime('%d/%m/%Y')),
        ('Gross Amount:', f"£{quote_data.get('gross_amount', 0):,.2f}"),
        ('Net Advance:', f"£{quote_data.get('net_advance', 0):,.2f}"),
        ('Interest Rate:', f"{quote_data.get('interest_rate', 0):.2f}%"),
        ('Loan Term:', f"{quote_data.get('loan_term', 0)} months"),
        ('Monthly Payment:', f"£{quote_data.get('monthly_payment', 0):,.2f}"),
        ('Total Interest:', f"£{quote_data.get('total_interest', 0):,.2f}"),
    ]
    
    for i, (key, value) in enumerate(details):
        table.cell(i, 0).text = key
        table.cell(i, 1).text = value
    
    # Add footer
    doc.add_paragraph()
    footer = doc.add_paragraph('This quote is subject to credit approval and full underwriting. Terms and conditions apply.')
    footer.alignment = 1  # Center alignment
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_file:
        doc.save(tmp_file.name)
        tmp_path = tmp_file.name
    
    # Read the content
    with open(tmp_path, 'rb') as f:
        docx_content = f.read()
    
    # Clean up
    os.unlink(tmp_path)
    
    return docx_content