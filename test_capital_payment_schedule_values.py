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
        'payment_timing': 'arrears',
    }
    result = calc.calculate_bridge_loan(params)
    schedule = result['detailed_payment_schedule']
    first_interest = currency_to_decimal(schedule[0]['interest_accrued'])
    second_refund = currency_to_decimal(schedule[1]['interest_refund'])
    assert first_interest == Decimal('20383.56')
    assert second_refund == Decimal('1972.61')


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
        'payment_timing': 'arrears',
    }
    result = calc.calculate_bridge_loan(params)
    schedule = result['detailed_payment_schedule']
    refund_total = sum(abs(currency_to_decimal(r['interest_refund'])) for r in schedule)
    assert refund_total.quantize(Decimal('0.01')) == Decimal(str(result['interestRefund'])).quantize(Decimal('0.01'))


def test_capital_payment_only_final_refund_formula():
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
        'payment_timing': 'arrears',
    }
    result = calc.calculate_bridge_loan(params)
    last = result['detailed_payment_schedule'][-2]
    refund = abs(currency_to_decimal(last['interest_refund']))
    retained = currency_to_decimal(last['interest_retained'])
    accrued = currency_to_decimal(last['interest_accrued'])
    assert accrued > 0
    assert refund.quantize(Decimal('0.01')) == (retained - accrued).quantize(Decimal('0.01'))


def test_capital_payment_only_advance_totals_match():
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
        'payment_timing': 'advance',
    }
    result = calc.calculate_bridge_loan(params)
    schedule = result['detailed_payment_schedule']
    total_accrued = sum(currency_to_decimal(r['interest_accrued']) for r in schedule)
    retained = Decimal(str(result['retainedInterest']))
    refund = Decimal(str(result['interestRefund']))
    summary_interest = Decimal(str(result['totalInterest']))
    assert total_accrued.quantize(Decimal('0.01')) == summary_interest.quantize(Decimal('0.01'))
    diff = (retained - refund - summary_interest).copy_abs()
    assert diff < Decimal('0.02')


def test_capital_outstanding_reduces_on_advance_payment():
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
        'payment_timing': 'advance',
    }
    result = calc.calculate_bridge_loan(params)
    schedule = result['detailed_payment_schedule']
    first = schedule[0]
    second = schedule[1]
    assert currency_to_decimal(first['capital_outstanding']) == Decimal('1800000')
    assert currency_to_decimal(second['capital_outstanding']) == Decimal('1600000')
