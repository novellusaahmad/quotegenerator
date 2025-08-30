import sys, types
from decimal import Decimal

# Minimal relativedelta stub to avoid external dependency
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
sys.modules.setdefault('dateutil', types.ModuleType('dateutil')).relativedelta = relativedelta_module
sys.modules['dateutil.relativedelta'] = relativedelta_module

import pytest
from calculations import LoanCalculator


def test_service_only_last_period_prorates_interest():
    calc = LoanCalculator()
    params = {
        'loan_type': 'bridge',
        'repayment_option': 'service_only',
        'gross_amount': 100000,
        'loan_term': 2,
        'annual_rate': 12,
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
        'payment_timing': 'arrears',
        'start_date': '2024-01-01'
    }
    result = calc.calculate_bridge_loan(params)
    schedule = result['payment_schedule']
    first_interest = Decimal(str(schedule[0]['interest']))
    second_interest = Decimal(str(schedule[1]['interest']))
    assert second_interest < first_interest
    expected_second = calc.calculate_simple_interest_by_days(
        Decimal('100000'), Decimal('12'), 29
    )
    assert float(second_interest) == pytest.approx(float(expected_second), rel=1e-6)
