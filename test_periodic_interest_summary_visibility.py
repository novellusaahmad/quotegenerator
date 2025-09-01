import sys, types
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
        day = min(
            other.day,
            [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
             31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]
        )
        return other.replace(year=year, month=month, day=day)
relativedelta_module.relativedelta = relativedelta
sys.modules['dateutil'] = types.ModuleType('dateutil')
sys.modules['dateutil'].relativedelta = relativedelta_module
sys.modules['dateutil.relativedelta'] = relativedelta_module

from calculations import LoanCalculator


@pytest.mark.parametrize("repayment_option", ['service_only', 'capital_payment_only', 'flexible_payment'])
@pytest.mark.parametrize("payment_frequency", ['monthly', 'quarterly'])
def test_periodic_interest_visible_and_correct(repayment_option, payment_frequency):
    calc = LoanCalculator()
    params = {
        'loan_type': 'bridge',
        'repayment_option': repayment_option,
        'gross_amount': 600000,
        'annual_rate': 12,
        'loan_term': 12,
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
        'payment_frequency': payment_frequency,
        'start_date': '2024-01-01',
    }
    if repayment_option == 'capital_payment_only':
        params['capital_repayment'] = 10000
    if repayment_option == 'flexible_payment':
        params['flexible_payment'] = 10000

    result = calc.calculate_bridge_loan(params)
    divisor = 12 if payment_frequency == 'monthly' else 4
    expected = 600000 * 0.12 / divisor

    assert result['periodicInterest'] == pytest.approx(expected, abs=0.01)
    assert result['monthlyInterestPayment'] == pytest.approx(600000 * 0.12 / 12, abs=0.01)
    assert result['quarterlyInterestPayment'] == pytest.approx(600000 * 0.12 / 4, abs=0.01)
    assert result['periodicInterest'] > 0
