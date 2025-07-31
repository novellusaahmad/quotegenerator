"""
Excel Generator for Novellus Loan Management System
"""
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
import tempfile
import os
from datetime import datetime

class NovellussExcelGenerator:
    """Excel generator for loan quotes and calculations"""
    
    def __init__(self):
        self.workbook = None
        self.worksheet = None
    
    def generate_quote_excel(self, quote_data, application_data=None):
        """Generate Excel quote document"""
        # Create new workbook
        self.workbook = openpyxl.Workbook()
        self.worksheet = self.workbook.active
        self.worksheet.title = "Loan Quote"
        
        # Set up styles
        title_font = Font(name='Arial', size=16, bold=True)
        header_font = Font(name='Arial', size=12, bold=True)
        normal_font = Font(name='Arial', size=10)
        
        # Add title
        self.worksheet['A1'] = "Novellus Finance - Loan Quote"
        self.worksheet['A1'].font = title_font
        self.worksheet['A1'].alignment = Alignment(horizontal='center')
        self.worksheet.merge_cells('A1:B1')
        
        # Add quote details
        row = 3
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
        
        for key, value in details:
            self.worksheet[f'A{row}'] = key
            self.worksheet[f'A{row}'].font = header_font
            self.worksheet[f'B{row}'] = value
            self.worksheet[f'B{row}'].font = normal_font
            row += 1
        
        # Auto-adjust column widths
        for column in self.worksheet.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            self.worksheet.column_dimensions[column_letter].width = adjusted_width
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            self.workbook.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        # Read the content
        with open(tmp_path, 'rb') as f:
            excel_content = f.read()
        
        # Clean up
        os.unlink(tmp_path)
        
        return excel_content
    
    def generate_payment_schedule_excel(self, payment_schedule, quote_data):
        """Generate Excel payment schedule"""
        # Create new workbook
        self.workbook = openpyxl.Workbook()
        self.worksheet = self.workbook.active
        self.worksheet.title = "Payment Schedule"
        
        # Set up styles
        title_font = Font(name='Arial', size=16, bold=True)
        header_font = Font(name='Arial', size=12, bold=True)
        normal_font = Font(name='Arial', size=10)
        
        # Add title
        self.worksheet['A1'] = "Novellus Finance - Payment Schedule"
        self.worksheet['A1'].font = title_font
        self.worksheet['A1'].alignment = Alignment(horizontal='center')
        self.worksheet.merge_cells('A1:F1')
        
        # Add headers
        headers = ['Payment #', 'Date', 'Opening Balance', 'Payment', 'Interest', 'Closing Balance']
        for col, header in enumerate(headers, 1):
            cell = self.worksheet.cell(row=3, column=col)
            cell.value = header
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center')
        
        # Add payment schedule data
        row = 4
        for i, payment in enumerate(payment_schedule, 1):
            self.worksheet.cell(row=row, column=1).value = i
            self.worksheet.cell(row=row, column=2).value = payment.get('date', '')
            self.worksheet.cell(row=row, column=3).value = f"£{payment.get('opening_balance', 0):,.2f}"
            self.worksheet.cell(row=row, column=4).value = f"£{payment.get('payment_amount', 0):,.2f}"
            self.worksheet.cell(row=row, column=5).value = f"£{payment.get('interest_amount', 0):,.2f}"
            self.worksheet.cell(row=row, column=6).value = f"£{payment.get('closing_balance', 0):,.2f}"
            row += 1
        
        # Auto-adjust column widths
        for column in self.worksheet.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 20)
            self.worksheet.column_dimensions[column_letter].width = adjusted_width
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            self.workbook.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        # Read the content
        with open(tmp_path, 'rb') as f:
            excel_content = f.read()
        
        # Clean up
        os.unlink(tmp_path)
        
        return excel_content