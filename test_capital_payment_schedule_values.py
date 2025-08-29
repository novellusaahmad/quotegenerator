import sys, types

relativedelta_module = types.ModuleType('relativedelta')
class relativedelta:
    def __init__(self, months=0):
        self.months = months
    def __radd__(self, other):
        from datetime import date
        month = other.month - 1 + self.months
        year = other.year + month // 12
        month = month % 12 + 1
        day = min(other.day, [31,29 if year %4==0 and (year%100!=0 or year%400==0) else 28,31,30,31,30,31,31,30,31,30,31][month-1])
        return other.replace(year=year, month=month, day=day)
relativedelta_module.relativedelta = relativedelta
sys.modules['dateutil'] = types.ModuleType('dateutil')
sys.modules['dateutil'].relativedelta = relativedelta_module
sys.modules['dateutil.relativedelta'] = relativedelta_module

from decimal import Decimal
from calculations import LoanCalculator

def currency_to_decimal(value):
    return Decimal(value.replace('£','').replace(',',''))

def test_capital_payment_only_interest_refund():
    calc = LoanCalculator()
    params = {
        'loan_type': 'bridge',
        'repayment_option': 'capital_payment_only',
        'gross_amount': 2000000,
        'loan_term': 12,
        'annual_rate': 12,
        'capital_repayment': 200000,
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
        'start_date': '2025-08-01',
        'property_value': 3000000,
    }
    result = calc.calculate_bridge_loan(params)
    schedule = result['detailed_payment_schedule']
    first_interest = currency_to_decimal(schedule[0]['interest_accrued'])
    second_refund = currency_to_decimal(schedule[1]['interest_refund'])
    assert first_interest == Decimal('20000.00')
    assert second_refund == Decimal('2000.00')


def test_capital_payment_only_refund_totals_match():
    calc = LoanCalculator()
    params = {
        'loan_type': 'bridge',
        'repayment_option': 'capital_payment_only',
        'gross_amount': 2000000,
        'loan_term': 12,
        'annual_rate': 12,
        'capital_repayment': 200000,
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
        'start_date': '2025-08-01',
        'property_value': 3000000,
    }
    result = calc.calculate_bridge_loan(params)
    schedule = result['detailed_payment_schedule']
    refund_total = sum(abs(currency_to_decimal(r['interest_refund'])) for r in schedule)
    assert refund_total.quantize(Decimal('0.01')) == Decimal(str(result['interestRefund'])).quantize(Decimal('0.01'))


def test_capital_payment_only_refund_equals_retained_minus_accrued():
    calc = LoanCalculator()
    params = {
        'loan_type': 'bridge',
        'repayment_option': 'capital_payment_only',
        'gross_amount': 2000000,
        'loan_term': 12,
        'annual_rate': 12,
        'capital_repayment': 200000,
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
        'start_date': '2025-08-01',
        'property_value': 3000000,
    }
    result = calc.calculate_bridge_loan(params)
    schedule = result['detailed_payment_schedule']
    for entry in schedule:
        retained = currency_to_decimal(entry['interest_retained'])
        accrued = currency_to_decimal(entry['interest_accrued'])
        refund = currency_to_decimal(entry['interest_refund'])
        assert refund.quantize(Decimal('0.01')) == (retained - accrued).quantize(Decimal('0.01'))
