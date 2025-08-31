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


def test_capital_only_summary_includes_monthly_interest():
    calc = LoanCalculator()
    params = {
        'loan_type': 'bridge',
        'repayment_option': 'capital_payment_only',
        'gross_amount': 2000000,
        'annual_rate': 12,
        'loan_term': 12,
        'capital_repayment': 10000,
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
        'property_value': 3000000,
        'start_date': '2024-01-01',
    }
    result = calc.calculate_bridge_loan(params)

    days_first_month = 31  # January has 31 days
    expected_monthly_interest = 2000000 * 0.12 / 365 * days_first_month
    assert result['periodicInterest'] == pytest.approx(expected_monthly_interest, abs=0.01)
    assert result['monthlyPayment'] == pytest.approx(10000, abs=0.01)
