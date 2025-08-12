import types
import sys
import os
from decimal import Decimal
import pytest

# Minimal relativedelta stub as in other tests
relativedelta_module = types.ModuleType('relativedelta')
class relativedelta:
    def __init__(self, months=0):
        self.months = months
    def __radd__(self, other):
        from datetime import date
        month = other.month - 1 + self.months
        year = other.year + month // 12
        month = month % 12 + 1
        day = min(other.day, [31,29 if year %4==0 and (year%100!=0 or year%400==0) else 28,
                              31,30,31,30,31,31,30,31,30,31][month-1])
        return other.replace(year=year, month=month, day=day)
relativedelta_module.relativedelta = relativedelta
sys.modules['dateutil'] = types.ModuleType('dateutil')
sys.modules['dateutil'].relativedelta = relativedelta_module
sys.modules['dateutil.relativedelta'] = relativedelta_module

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calculations import LoanCalculator


def test_ltv_target_capital_payment_only():
    calc = LoanCalculator()
    gross_amount = Decimal('100000')
    property_value = Decimal('200000')
    loan_term = 10
    target_ltv = Decimal('40')

    target_balance = property_value * target_ltv / Decimal('100')
    months = loan_term - 2  # exclude interest retention and final balloon month
    monthly_capital = (gross_amount - target_balance) / months

    params = {
        'loan_type': 'bridge',
        'repayment_option': 'capital_payment_only',
        'gross_amount': float(gross_amount),
        'property_value': float(property_value),
        'loan_term': loan_term,
        'annual_rate': 12,
        'capital_repayment': float(monthly_capital),
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
    }
    result = calc.calculate_bridge_loan(params)

    assert result['startLTV'] == pytest.approx(50.0)
    assert result['endLTV'] == pytest.approx(float(target_ltv))
