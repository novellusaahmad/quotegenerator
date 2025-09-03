import sys, types
import pytest

# Minimal relativedelta stub
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

from report_utils import generate_report_schedule
from calculations import LoanCalculator

@pytest.mark.parametrize("repayment_option,payment_frequency,payment_timing,expected", [
    ('service_only', 'monthly', 'arrears', 'Monthly in Arrears'),
    ('service_and_capital', 'monthly', 'advance', 'Monthly in Advance'),
    ('capital_payment_only', 'quarterly', 'arrears', 'Quarterly in Arrears'),
    ('flexible_payment', 'quarterly', 'advance', 'Quarterly in Advance'),
])
def test_interest_payment_timing_in_summary(repayment_option, payment_frequency, payment_timing, expected):
    params = {
        'loan_type': 'bridge',
        'repayment_option': repayment_option,
        'gross_amount': 100000,
        'annual_rate': 12,
        'loan_term': 12,
        'payment_frequency': payment_frequency,
        'payment_timing': payment_timing,
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
        'start_date': '2024-01-01',
    }
    if repayment_option == 'service_and_capital':
        params['capital_repayment'] = 10000
    if repayment_option == 'capital_payment_only':
        params['capital_repayment'] = 10000
    if repayment_option == 'flexible_payment':
        params['flexible_payment'] = 2000
    _, summary = generate_report_schedule(params)
    assert summary['interestPaymentTiming'] == expected


@pytest.mark.parametrize("repayment_option,payment_frequency,payment_timing,expected", [
    ('service_only', 'monthly', 'arrears', 'Monthly in Arrears'),
    ('service_and_capital', 'monthly', 'advance', 'Monthly in Advance'),
    ('capital_payment_only', 'quarterly', 'arrears', 'Quarterly in Arrears'),
    ('flexible_payment', 'quarterly', 'advance', 'Quarterly in Advance'),
])
def test_interest_payment_timing_in_loan_summary(repayment_option, payment_frequency, payment_timing, expected):
    params = {
        'loan_type': 'bridge',
        'repayment_option': repayment_option,
        'gross_amount': 100000,
        'annual_rate': 12,
        'loan_term': 12,
        'payment_frequency': payment_frequency,
        'payment_timing': payment_timing,
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
        'start_date': '2024-01-01',
    }
    if repayment_option == 'service_and_capital':
        params['capital_repayment'] = 10000
    if repayment_option == 'capital_payment_only':
        params['capital_repayment'] = 10000
    if repayment_option == 'flexible_payment':
        params['flexible_payment'] = 2000
    calc = LoanCalculator()
    result = calc.calculate_bridge_loan(params)
    assert result['interestPaymentTiming'] == expected
