#!/usr/bin/env python3
"""
Simple Report Generator - Working Alternative to BIRT
Generates actual PDF and Excel reports from loan data
"""

import json
import os
import re
import sys
from decimal import Decimal, InvalidOperation
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
import xlsxwriter
from models import LoanSummary, PaymentSchedule
from app import db
from utils import get_currency_symbol

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

            # Determine currency formatting
            currency_symbol = loan.currency_symbol or get_currency_symbol(loan.currency or 'GBP')
            if currency_symbol == '£':
                currency_code = '£#,##0.00'
            elif currency_symbol == '€':
                currency_code = '€#,##0.00'
            elif currency_symbol == '$':
                currency_code = '$#,##0.00'
            else:
                currency_code = f'"{currency_symbol}"#,##0.00'

            currency_format = workbook.add_format({
                'num_format': currency_code,
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

            # Build detailed payment schedule worksheet if data exists
            schedule_records = (
                PaymentSchedule.query
                .filter_by(loan_summary_id=loan_id)
                .order_by(PaymentSchedule.period_number)
                .all()
            )

            schedule_sheet = workbook.add_worksheet('Detailed Payment Schedule')
            schedule_sheet.freeze_panes(1, 0)

            # Common formats for schedule
            schedule_header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#f8f9fa',
                'border': 1,
                'align': 'center',
                'valign': 'vcenter'
            })
            text_left = workbook.add_format({'border': 1, 'align': 'left', 'valign': 'vcenter'})
            text_center = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})
            number_center = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter', 'num_format': '0'})
            currency_cell = workbook.add_format({'border': 1, 'num_format': currency_code, 'valign': 'vcenter'})
            bold_right = workbook.add_format({'border': 1, 'bold': True, 'align': 'right', 'valign': 'vcenter'})
            bold_center = workbook.add_format({'border': 1, 'bold': True, 'align': 'center', 'valign': 'vcenter'})
            bold_currency = workbook.add_format({'border': 1, 'bold': True, 'num_format': currency_code, 'valign': 'vcenter'})

            def to_decimal(value):
                if value in (None, '', '—'):
                    return None
                if isinstance(value, Decimal):
                    return value
                if isinstance(value, (int, float)):
                    try:
                        return Decimal(str(value))
                    except (ValueError, InvalidOperation):
                        return None
                try:
                    value_str = str(value).strip()
                except Exception:
                    return None
                if not value_str:
                    return None
                cleaned = re.sub(r'[^0-9.,\-]', '', value_str)
                if not cleaned:
                    return None
                if ',' in cleaned and '.' in cleaned:
                    if cleaned.rfind('.') > cleaned.rfind(','):
                        cleaned = cleaned.replace(',', '')
                    else:
                        cleaned = cleaned.replace('.', '')
                        cleaned = cleaned.replace(',', '.')
                elif cleaned.count(',') > 0:
                    if cleaned.count(',') > 1:
                        parts = cleaned.split(',')
                        cleaned = ''.join(parts[:-1]) + '.' + parts[-1]
                    else:
                        cleaned = cleaned.replace(',', '.')
                elif cleaned.count('.') > 1:
                    parts = cleaned.split('.')
                    cleaned = ''.join(parts[:-1]) + '.' + parts[-1]
                try:
                    return Decimal(cleaned)
                except InvalidOperation:
                    return None

            def pick_value(entry, keys, fallback=''):
                if not isinstance(entry, dict):
                    entry = {}
                for key in keys:
                    value = entry.get(key)
                    if value not in (None, ''):
                        return value
                return fallback

            def get_currency_value(entry, keys, fallback=None):
                if not isinstance(entry, dict):
                    entry = {}
                for key in keys:
                    if key in entry and entry[key] not in (None, ''):
                        candidate = to_decimal(entry[key])
                        if candidate is not None:
                            return candidate
                if fallback not in (None, ''):
                    return to_decimal(fallback)
                return None

            def parse_days(entry, keys, fallback=None):
                raw = pick_value(entry, keys, fallback)
                try:
                    return int(str(raw)) if raw not in (None, '') else None
                except (ValueError, TypeError):
                    try:
                        return int(float(str(raw)))
                    except (ValueError, TypeError):
                        return None

            def clean_interest_calc(value):
                if not value:
                    return ''
                text = str(value)
                text = re.sub(r'\s*\+\s*fees', '', text, flags=re.IGNORECASE)
                return re.sub(r'[£€$]', currency_symbol, text)

            repayment_option = (loan.repayment_option or '').lower()

            if not schedule_records:
                schedule_sheet.write(0, 0, 'No payment schedule data is available for this loan.', text_left)
            else:
                schedule_entries = []
                for record in schedule_records:
                    try:
                        entry = json.loads(record.schedule_data) if record.schedule_data else {}
                    except (ValueError, TypeError):
                        entry = {}
                    schedule_entries.append((entry or {}, record))

                def write_table(headers, rows, column_formats, totals=None, total_formats=None, column_widths=None):
                    for col_idx, header in enumerate(headers):
                        schedule_sheet.write(0, col_idx, header, schedule_header_format)
                    if column_widths:
                        for idx, width in enumerate(column_widths):
                            schedule_sheet.set_column(idx, idx, width)
                    for row_idx, row_values in enumerate(rows, start=1):
                        for col_idx, value in enumerate(row_values):
                            fmt = column_formats[col_idx]
                            schedule_sheet.write(row_idx, col_idx, value, fmt)
                    if totals:
                        total_row_index = len(rows) + 1
                        formats = total_formats or column_formats
                        for col_idx, value in enumerate(totals):
                            fmt = formats[col_idx]
                            schedule_sheet.write(total_row_index, col_idx, value, fmt)

                if repayment_option == 'service_only':
                    headers = [
                        'Start of Period',
                        'End of Period',
                        'Days Held',
                        'Opening Balance',
                        'Interest Calculation',
                        'Interest Serviced'
                    ]
                    rows = []
                    total_interest = Decimal('0')
                    total_days = 0
                    for entry, record in schedule_entries:
                        start = pick_value(entry, ['start_period', 'startPeriod', 'period_start', 'start_of_period', 'periodStart'])
                        end = pick_value(entry, ['end_period', 'endPeriod', 'period_end', 'end_of_period', 'periodEnd'])
                        days = parse_days(entry, ['days_held', 'daysHeld', 'days'])
                        opening = get_currency_value(entry, ['opening_balance', 'openingBalance'], record.opening_balance)
                        interest_calc = clean_interest_calc(pick_value(entry, ['interest_calculation', 'interestCalculation'], record.interest_calculation))
                        interest_amount = get_currency_value(entry, ['interest_amount', 'interestAmount', 'interest_serviced', 'interest_payment', 'interest'], record.interest_amount)

                        rows.append([
                            start or '',
                            end or '',
                            days,
                            float(opening) if opening is not None else None,
                            interest_calc or '',
                            float(interest_amount) if interest_amount is not None else None
                        ])

                        if interest_amount is not None:
                            total_interest += interest_amount
                        if days:
                            total_days += days

                    column_formats = [text_center, text_center, number_center, currency_cell, text_center, currency_cell]
                    totals = [
                        'Total',
                        '',
                        total_days if total_days else None,
                        None,
                        None,
                        float(total_interest) if total_interest else None
                    ]
                    total_formats = [bold_right, bold_center, bold_center, bold_currency, bold_center, bold_currency]
                    write_table(headers, rows, column_formats, totals, total_formats, [18, 18, 12, 18, 26, 18])

                elif repayment_option == 'service_and_capital':
                    headers = [
                        'Period', 'Start of Period', 'End of Period', 'Days Held', 'Capital Outstanding',
                        'Annual Interest %', 'Interest Factor P.D.', 'Scheduled Repayment', 'Total Repayment',
                        'Interest Accrued', 'Interest Retained', 'Interest Refund', 'Running LTV'
                    ]
                    rows = []
                    total_scheduled = Decimal('0')
                    total_repayment = Decimal('0')
                    total_accrued = Decimal('0')
                    total_retained = Decimal('0')
                    total_refund = Decimal('0')
                    total_days = 0
                    for index, (entry, record) in enumerate(schedule_entries, start=1):
                        capital = get_currency_value(entry, ['capital_outstanding', 'capitalOutstanding', 'opening_balance', 'openingBalance'], record.opening_balance)
                        scheduled = get_currency_value(entry, ['scheduled_repayment', 'scheduledRepayment', 'scheduled_payment'], record.total_payment)
                        total_repay = get_currency_value(entry, ['total_repayment', 'totalRepayment', 'payment_total'], record.total_payment)
                        accrued = get_currency_value(entry, ['interest_accrued', 'interestAccrued'], record.interest_amount)
                        retained = get_currency_value(entry, ['interest_retained', 'retained_interest'])
                        refund = get_currency_value(entry, ['interest_refund', 'interest_refunded'])
                        days = parse_days(entry, ['days_held', 'daysHeld', 'days'])

                        rows.append([
                            index,
                            pick_value(entry, ['start_period', 'startPeriod', 'period_start', 'start_of_period', 'periodStart']) or '',
                            pick_value(entry, ['end_period', 'endPeriod', 'period_end', 'end_of_period', 'periodEnd']) or '',
                            days,
                            float(capital) if capital is not None else None,
                            pick_value(entry, ['annual_interest_rate', 'interest_rate']) or '',
                            pick_value(entry, ['interest_pa', 'interest_factor_pd']) or '',
                            float(scheduled) if scheduled is not None else None,
                            float(total_repay) if total_repay is not None else None,
                            float(accrued) if accrued is not None else None,
                            float(retained) if retained is not None else None,
                            float(refund) if refund is not None else None,
                            pick_value(entry, ['running_ltv', 'runningLtv']) or ''
                        ])

                        if scheduled is not None:
                            total_scheduled += scheduled
                        if total_repay is not None:
                            total_repayment += total_repay
                        if accrued is not None:
                            total_accrued += accrued
                        if retained is not None:
                            total_retained += retained
                        if refund is not None:
                            total_refund += refund
                        if days:
                            total_days += days

                    column_formats = [number_center, text_center, text_center, number_center, currency_cell,
                                       text_center, text_center, currency_cell, currency_cell, currency_cell,
                                       currency_cell, currency_cell, text_center]
                    totals = [
                        'Total', '', '', total_days if total_days else None, None, None, None,
                        float(total_scheduled) if total_scheduled else None,
                        float(total_repayment) if total_repayment else None,
                        float(total_accrued) if total_accrued else None,
                        float(total_retained) if total_retained else None,
                        float(total_refund) if total_refund else None,
                        ''
                    ]
                    total_formats = [bold_right, bold_center, bold_center, bold_center, bold_currency, bold_center, bold_center,
                                     bold_currency, bold_currency, bold_currency, bold_currency, bold_currency, bold_center]
                    write_table(headers, rows, column_formats, totals, total_formats,
                                [10, 18, 18, 12, 18, 16, 18, 18, 18, 18, 18, 18, 14])

                elif repayment_option == 'flexible_payment':
                    headers = [
                        'Period', 'Start of Period', 'End of Period', 'Days Held', 'Capital Outstanding',
                        'Annual Interest %', 'Interest Factor P.D.', 'Total Repayment', 'Capital Repayment',
                        'Interest Accrued', 'Interest Retained', 'Interest Refund', 'Running LTV'
                    ]
                    rows = []
                    total_repayment = Decimal('0')
                    total_capital = Decimal('0')
                    total_accrued = Decimal('0')
                    total_retained = Decimal('0')
                    total_refund = Decimal('0')
                    total_days = 0
                    for index, (entry, record) in enumerate(schedule_entries, start=1):
                        capital = get_currency_value(entry, ['capital_outstanding', 'capitalOutstanding', 'opening_balance', 'openingBalance'], record.opening_balance)
                        total_repay = get_currency_value(entry, ['total_repayment', 'totalRepayment', 'payment_total'], record.total_payment)
                        capital_repay = get_currency_value(entry, ['capital_repayment', 'capitalRepayment', 'principal_payment', 'principal'], record.principal_payment)
                        accrued = get_currency_value(entry, ['interest_accrued', 'interestAccrued'], record.interest_amount)
                        retained = get_currency_value(entry, ['interest_retained', 'retained_interest'])
                        refund = get_currency_value(entry, ['interest_refund', 'interest_refunded'])
                        days = parse_days(entry, ['days_held', 'daysHeld', 'days'])

                        rows.append([
                            index,
                            pick_value(entry, ['start_period', 'startPeriod', 'period_start', 'start_of_period', 'periodStart']) or '',
                            pick_value(entry, ['end_period', 'endPeriod', 'period_end', 'end_of_period', 'periodEnd']) or '',
                            days,
                            float(capital) if capital is not None else None,
                            pick_value(entry, ['annual_interest_rate', 'interest_rate']) or '',
                            pick_value(entry, ['interest_pa', 'interest_factor_pd']) or '',
                            float(total_repay) if total_repay is not None else None,
                            float(capital_repay) if capital_repay is not None else None,
                            float(accrued) if accrued is not None else None,
                            float(retained) if retained is not None else None,
                            float(refund) if refund is not None else None,
                            pick_value(entry, ['running_ltv', 'runningLtv']) or ''
                        ])

                        if total_repay is not None:
                            total_repayment += total_repay
                        if capital_repay is not None:
                            total_capital += capital_repay
                        if accrued is not None:
                            total_accrued += accrued
                        if retained is not None:
                            total_retained += retained
                        if refund is not None:
                            total_refund += refund
                        if days:
                            total_days += days

                    column_formats = [number_center, text_center, text_center, number_center, currency_cell,
                                       text_center, text_center, currency_cell, currency_cell, currency_cell,
                                       currency_cell, currency_cell, text_center]
                    totals = [
                        'Total', '', '', total_days if total_days else None, None, None, None,
                        float(total_repayment) if total_repayment else None,
                        float(total_capital) if total_capital else None,
                        float(total_accrued) if total_accrued else None,
                        float(total_retained) if total_retained else None,
                        float(total_refund) if total_refund else None,
                        ''
                    ]
                    total_formats = [bold_right, bold_center, bold_center, bold_center, bold_currency, bold_center, bold_center,
                                     bold_currency, bold_currency, bold_currency, bold_currency, bold_currency, bold_center]
                    write_table(headers, rows, column_formats, totals, total_formats,
                                [10, 18, 18, 12, 18, 16, 18, 18, 18, 18, 18, 18, 14])

                elif repayment_option == 'capital_payment_only':
                    headers = [
                        'Period', 'Start of Period', 'End of Period', 'Days Held', 'Capital Outstanding',
                        'Annual Interest %', 'Interest Factor P.D.', 'Scheduled Repayment', 'Interest Accrued',
                        'Interest Retained', 'Interest Refund', 'Running LTV'
                    ]
                    rows = []
                    total_scheduled = Decimal('0')
                    total_accrued = Decimal('0')
                    total_retained = Decimal('0')
                    total_refund = Decimal('0')
                    total_days = 0
                    for index, (entry, record) in enumerate(schedule_entries, start=1):
                        capital = get_currency_value(entry, ['capital_outstanding', 'capitalOutstanding', 'opening_balance', 'openingBalance'], record.opening_balance)
                        scheduled = get_currency_value(entry, ['scheduled_repayment', 'scheduledRepayment', 'scheduled_payment'], record.total_payment)
                        accrued = get_currency_value(entry, ['interest_accrued', 'interestAccrued'], record.interest_amount)
                        retained = get_currency_value(entry, ['interest_retained', 'retained_interest'])
                        refund = get_currency_value(entry, ['interest_refund', 'interest_refunded'])
                        days = parse_days(entry, ['days_held', 'daysHeld', 'days'])

                        rows.append([
                            index,
                            pick_value(entry, ['start_period', 'startPeriod', 'period_start', 'start_of_period', 'periodStart']) or '',
                            pick_value(entry, ['end_period', 'endPeriod', 'period_end', 'end_of_period', 'periodEnd']) or '',
                            days,
                            float(capital) if capital is not None else None,
                            pick_value(entry, ['annual_interest_rate', 'interest_rate']) or '',
                            pick_value(entry, ['interest_pa', 'interest_factor_pd']) or '',
                            float(scheduled) if scheduled is not None else None,
                            float(accrued) if accrued is not None else None,
                            float(retained) if retained is not None else None,
                            float(refund) if refund is not None else None,
                            pick_value(entry, ['running_ltv', 'runningLtv']) or ''
                        ])

                        if scheduled is not None:
                            total_scheduled += scheduled
                        if accrued is not None:
                            total_accrued += accrued
                        if retained is not None:
                            total_retained += retained
                        if refund is not None:
                            total_refund += refund
                        if days:
                            total_days += days

                    column_formats = [number_center, text_center, text_center, number_center, currency_cell,
                                       text_center, text_center, currency_cell, currency_cell, currency_cell,
                                       currency_cell, text_center]
                    totals = [
                        'Total', '', '', total_days if total_days else None, None, None, None,
                        float(total_scheduled) if total_scheduled else None,
                        float(total_accrued) if total_accrued else None,
                        float(total_retained) if total_retained else None,
                        float(total_refund) if total_refund else None,
                        ''
                    ]
                    total_formats = [bold_right, bold_center, bold_center, bold_center, bold_currency, bold_center, bold_center,
                                     bold_currency, bold_currency, bold_currency, bold_currency, bold_center]
                    write_table(headers, rows, column_formats, totals, total_formats,
                                [10, 18, 18, 12, 18, 16, 18, 18, 18, 18, 18, 14])

                else:
                    headers = [
                        'Payment Date', 'Opening Balance', 'Tranche Release', 'Interest Calculation',
                        'Interest Amount', 'Interest Saving', 'Principal Payment', 'Total Payment',
                        'Closing Balance', 'Balance Change'
                    ]
                    rows = []
                    for entry, record in schedule_entries:
                        payment_date = pick_value(entry, ['payment_date', 'paymentDate', 'date']) or ''
                        opening = get_currency_value(entry, ['opening_balance', 'openingBalance'], record.opening_balance)
                        tranche = get_currency_value(entry, ['tranche_release', 'tranche', 'drawdown', 'drawdown_amount'], record.tranche_release)
                        interest_calc = clean_interest_calc(pick_value(entry, ['interest_calculation', 'interestCalculation'], record.interest_calculation))
                        interest_amount = get_currency_value(entry, ['interest_amount', 'interestAmount', 'interest'], record.interest_amount)
                        interest_saving = get_currency_value(entry, ['interest_saving', 'interestSaving'])
                        principal = get_currency_value(entry, ['principal_payment', 'principal'], record.principal_payment)
                        total_payment = get_currency_value(entry, ['total_payment', 'payment_total'], record.total_payment)
                        closing = get_currency_value(entry, ['closing_balance', 'closingBalance', 'balance'], record.closing_balance)
                        balance_change = pick_value(entry, ['balance_change', 'balanceChange'], record.balance_change) or ''

                        rows.append([
                            payment_date,
                            float(opening) if opening is not None else None,
                            float(tranche) if tranche is not None else None,
                            interest_calc,
                            float(interest_amount) if interest_amount is not None else None,
                            float(interest_saving) if interest_saving is not None else None,
                            float(principal) if principal is not None else None,
                            float(total_payment) if total_payment is not None else None,
                            float(closing) if closing is not None else None,
                            balance_change
                        ])

                    column_formats = [text_center, currency_cell, currency_cell, text_center, currency_cell,
                                       currency_cell, currency_cell, currency_cell, currency_cell, text_center]
                    write_table(headers, rows, column_formats, column_widths=[16, 18, 18, 30, 18, 18, 18, 18, 18, 18])

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