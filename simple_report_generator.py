#!/usr/bin/env python3
"""
Simple Report Generator - Working Alternative to BIRT
Generates actual PDF and Excel reports from loan data
"""

import os
import sys
from decimal import Decimal
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
import xlsxwriter
from models import LoanSummary, PaymentSchedule
from app import db

class WorkingReportGenerator:
    """A working report generator that actually produces reports"""
    
    def __init__(self):
        self.output_dir = "reports_output"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_loan_summary_pdf(self, loan_id):
        """Generate an actual PDF report for a loan"""
        try:
            # Get loan data
            loan = LoanSummary.query.get(loan_id)
            if not loan:
                return {'success': False, 'error': 'Loan not found'}
            
            # Create PDF file
            filename = f"loan_summary_{loan_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#B8860B'),
                alignment=1  # Center
            )
            story.append(Paragraph("Novellus Loan Summary Report", title_style))
            story.append(Spacer(1, 20))
            
            # Loan details table
            show_end_ltv = not (loan.loan_type == 'bridge' and str(loan.repayment_option) in ('none', 'retained', 'retained_interest'))
            loan_data = [
                ['Field', 'Value'],
                ['Loan Name', loan.loan_name or 'N/A'],
                ['Loan Type', loan.loan_type or 'N/A'],
                ['Gross Amount', f"£{float(loan.gross_amount or 0):,.2f}"],
                ['Net Advance', f"£{float(loan.net_advance or 0):,.2f}"],
                ['Total Interest', f"£{float(loan.total_interest or 0):,.2f}"],
                ['Property Value', f"£{float(loan.property_value or 0):,.2f}"],
                ['Start LTV', f"{float(loan.start_ltv or 0):.2f}%"],
            ]
            if show_end_ltv:
                loan_data.append(['End LTV', f"{float(loan.end_ltv or 0):.2f}%"])
            loan_data.extend([
                ['Loan Term (Months)', str(getattr(loan, 'loan_term_months', getattr(loan, 'loan_term', 'N/A')))],
                ['Interest Rate', f"{float(loan.interest_rate or 0):.2f}%"],
                ['Created Date', loan.created_at.strftime('%Y-%m-%d %H:%M') if loan.created_at else 'N/A']
            ])
            
            table = Table(loan_data, colWidths=[2.5*inch, 3*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#B8860B')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 30))
            
            # Build PDF
            doc.build(story)
            
            return {
                'success': True,
                'filepath': filepath,
                'filename': filename,
                'message': f'PDF report generated successfully for loan {loan_id}'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'PDF generation failed: {str(e)}'}
    
    def generate_loan_summary_excel(self, loan_id):
        """Generate an actual Excel report for a loan"""
        try:
            # Get loan data
            loan = LoanSummary.query.get(loan_id)
            if not loan:
                return {'success': False, 'error': 'Loan not found'}
            
            # Create Excel file
            filename = f"loan_summary_{loan_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            filepath = os.path.join(self.output_dir, filename)
            
            workbook = xlsxwriter.Workbook(filepath)
            worksheet = workbook.add_worksheet('Loan Summary')
            
            # Formats
            header_format = workbook.add_format({
                'bold': True,
                'font_color': 'white',
                'bg_color': '#B8860B',
                'border': 1
            })
            
            data_format = workbook.add_format({
                'border': 1,
                'align': 'left'
            })
            
            currency_format = workbook.add_format({
                'num_format': '£#,##0.00',
                'border': 1
            })
            
            # Write headers
            worksheet.write('A1', 'Field', header_format)
            worksheet.write('B1', 'Value', header_format)
            
            # Write data
            row = 1
            show_end_ltv = not (loan.loan_type == 'bridge' and str(loan.repayment_option) in ('none', 'retained', 'retained_interest'))
            data_rows = [
                ('Loan Name', loan.loan_name or 'N/A', data_format),
                ('Loan Type', loan.loan_type or 'N/A', data_format),
                ('Gross Amount', float(loan.gross_amount or 0), currency_format),
                ('Net Advance', float(loan.net_advance or 0), currency_format),
                ('Total Interest', float(loan.total_interest or 0), currency_format),
                ('Property Value', float(loan.property_value or 0), currency_format),
                ('Start LTV', f"{float(loan.start_ltv or 0):.2f}%", data_format),
            ]
            if show_end_ltv:
                data_rows.append(('End LTV', f"{float(loan.end_ltv or 0):.2f}%", data_format))
            data_rows.extend([
                ('Loan Term (Months)', getattr(loan, 'loan_term_months', getattr(loan, 'loan_term', 'N/A')), data_format),
                ('Interest Rate', f"{float(loan.interest_rate or 0):.2f}%", data_format),
                ('Created Date', loan.created_at.strftime('%Y-%m-%d %H:%M') if loan.created_at else 'N/A', data_format)
            ])
            
            for field, value, fmt in data_rows:
                worksheet.write(row, 0, field, data_format)
                worksheet.write(row, 1, value, fmt)
                row += 1
            
            # Adjust column widths
            worksheet.set_column('A:A', 20)
            worksheet.set_column('B:B', 25)
            
            workbook.close()
            
            return {
                'success': True,
                'filepath': filepath,
                'filename': filename,
                'message': f'Excel report generated successfully for loan {loan_id}'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Excel generation failed: {str(e)}'}

# Create global instance
working_report_generator = WorkingReportGenerator()

if __name__ == "__main__":
    # Test the report generator
    print("Testing Working Report Generator...")
    
    # Create test report
    with db.app.app_context():
        # Get first loan for testing
        loan = LoanSummary.query.first()
        if loan:
            print(f"Testing with loan ID: {loan.id}")
            
            # Test PDF generation
            pdf_result = working_report_generator.generate_loan_summary_pdf(loan.id)
            print(f"PDF Result: {pdf_result}")
            
            # Test Excel generation
            excel_result = working_report_generator.generate_loan_summary_excel(loan.id)
            print(f"Excel Result: {excel_result}")
            
        else:
            print("No loans found in database - cannot test")