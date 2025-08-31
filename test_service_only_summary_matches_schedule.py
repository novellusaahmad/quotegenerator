import sys, types
from decimal import Decimal

# Provide minimal stub for dateutil.relativedelta to avoid external dependency
relativedelta_module = types.ModuleType('relativedelta')
class relativedelta:
    def __init__(self, months=0):
        self.months = months
    def __radd__(self, other):
        from datetime import date
        month = other.month - 1 + self.months
        year = other.year + month // 12
        month = month % 12 + 1
        day = min(other.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                              31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
        return other.replace(year=year, month=month, day=day)
relativedelta_module.relativedelta = relativedelta
sys.modules['dateutil'] = types.ModuleType('dateutil')
sys.modules['dateutil'].relativedelta = relativedelta_module
sys.modules['dateutil.relativedelta'] = relativedelta_module

from calculations import LoanCalculator

def _currency_to_decimal(value: str) -> Decimal:
    return Decimal(value.replace('£', '').replace(',', ''))

def test_service_only_summary_matches_schedule():
    calc = LoanCalculator()
    params = {
        'loan_type': 'bridge',
        'repayment_option': 'service_only',
        'gross_amount': 100000,
        'loan_term': 12,
        'annual_rate': 12,
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
        'start_date': '2025-08-01',
        'payment_timing': 'advance',
    }
    result = calc.calculate_bridge_loan(params)
    schedule = result['detailed_payment_schedule']
    interest_total = sum(_currency_to_decimal(r.get('interest_accrued', r['interest_amount'])) for r in schedule)
    diff = (interest_total - Decimal(str(result['totalInterest']))).copy_abs()
    assert diff < Decimal('0.02')
    diff_interest_only = (Decimal(str(result['interestOnlyTotal'])) - interest_total).copy_abs()
    assert diff_interest_only < Decimal('0.02')
