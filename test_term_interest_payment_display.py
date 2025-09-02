import sys, types
from decimal import Decimal
import pytest

# Provide minimal stub for dateutil.relativedelta
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


@pytest.mark.parametrize("repayment_option", ['service_only', 'service_and_capital'])
@pytest.mark.parametrize("amount_input_type", ['gross', 'net'])
@pytest.mark.parametrize("payment_frequency", ['monthly', 'quarterly'])
def test_term_summary_interest_payments_use_gross_amount(repayment_option, amount_input_type, payment_frequency):
    calc = LoanCalculator()
    params = {
        'loan_type': 'term',
        'repayment_option': repayment_option,
        'annual_rate': 12,
        'loan_term': 12,
        'payment_frequency': payment_frequency,
        'payment_timing': 'arrears',
        'start_date': '2024-01-01',
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
    }
    if amount_input_type == 'gross':
        params['gross_amount'] = 600000
    else:
        params['amount_input_type'] = 'net'
        params['net_amount'] = 600000
    if repayment_option == 'service_and_capital':
        params['capital_repayment'] = 5000

    result = calc.calculate_term_loan(params)
    gross = Decimal(str(result['grossAmount']))
    expected_monthly = gross * Decimal('0.12') / Decimal('12')
    expected_quarterly = gross * Decimal('0.12') / Decimal('4')
    assert result['monthlyInterestPayment'] == pytest.approx(float(expected_monthly), abs=0.01)
    assert result['quarterlyInterestPayment'] == pytest.approx(float(expected_quarterly), abs=0.01)
    expected_periodic = expected_monthly if payment_frequency == 'monthly' else expected_quarterly
    assert result['periodicInterest'] == pytest.approx(float(expected_periodic), abs=0.01)
