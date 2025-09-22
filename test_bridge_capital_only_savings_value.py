from decimal import Decimal
import pytest
import sys, types

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


def test_capital_payment_only_uses_actual_days_for_savings():
    calc = LoanCalculator()
    params = {
        'loan_type': 'bridge',
        'repayment_option': 'capital_payment_only',
        'gross_amount': 2000000,
        'annual_rate': 12,
        'loan_term': 12,
        'capital_repayment': 30000,
        'arrangement_fee_rate': 2,
        'legal_fees': 3000,
        'site_visit_fee': 5000,
        'title_insurance_rate': Decimal('0.168'),
        'start_date': '2025-08-28',
        'payment_timing': 'arrears',
    }
    result = calc.calculate_bridge_loan(params)
    assert result['interestSavings'] == pytest.approx(19785.21, abs=0.02)
    assert result['totalInterest'] == pytest.approx(220214.79, abs=0.02)

    schedule = result.get('detailed_payment_schedule', [])
    total_savings = sum(
        Decimal(entry['interest_saving'].replace('£', '').replace(',', ''))
        for entry in schedule
    )
    assert float(total_savings) == pytest.approx(result['interestSavings'], abs=0.02)
