import types
import sys
import os
from decimal import Decimal
import pytest

# Setup minimal relativedelta stub for tests if needed (similar to other tests)
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


def parse_currency(value):
    if isinstance(value, (int, float, Decimal)):
        return Decimal(str(value))
    return Decimal(str(value).replace('£','').replace(',',''))


def test_capital_payment_only_end_ltv():
    calc = LoanCalculator()
    params = {
        'loan_type': 'bridge',
        'repayment_option': 'capital_payment_only',
        'gross_amount': 100000,
        'property_value': 200000,
        'loan_term': 10,
        'annual_rate': 12,
        'capital_repayment': 10000,
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
    }
    result = calc.calculate_bridge_loan(params)
    assert result['startLTV'] == pytest.approx(50.0)

    assert 'detailed_payment_schedule' in result and result['detailed_payment_schedule'], "schedule missing"
    last = result['detailed_payment_schedule'][-1]
    opening_balance = parse_currency(last.get('opening_balance') or last.get('openingBalance'))
    expected_end_ltv = float((opening_balance / Decimal('200000')) * 100)

    assert result['endLTV'] == pytest.approx(expected_end_ltv)
    # Alias fields should mirror the primary LTV values
    assert result['startLtv'] == pytest.approx(result['startLTV'])
    assert result['endLtv'] == pytest.approx(result['endLTV'])


def test_flexible_payment_end_ltv_matches_schedule():
    calc = LoanCalculator()
    params = {
        'loan_type': 'bridge',
        'repayment_option': 'flexible_payment',
        'gross_amount': 100000,
        'property_value': 200000,
        'loan_term': 12,
        'annual_rate': 12,
        'flexible_payment': 2000,
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
        'start_date': '2024-01-01',
    }
    result = calc.calculate_bridge_loan(params)
    assert 'detailed_payment_schedule' in result and result['detailed_payment_schedule'], "schedule missing"
    last = result['detailed_payment_schedule'][-1]
    closing_balance = parse_currency(last.get('closing_balance') or last.get('closingBalance'))
    expected_end_ltv = float((closing_balance / Decimal('200000')) * 100)
    assert result['endLTV'] == pytest.approx(expected_end_ltv)
    # Ensure camelCase alias is also updated
    assert result['endLtv'] == pytest.approx(expected_end_ltv)


def test_flexible_payment_zero_end_ltv_increases():
    calc = LoanCalculator()
    params = {
        'loan_type': 'bridge',
        'repayment_option': 'flexible_payment',
        'gross_amount': 100000,
        'property_value': 200000,
        'loan_term': 12,
        'annual_rate': 12,
        'flexible_payment': 0,
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
        'start_date': '2024-01-01',
    }
    result = calc.calculate_bridge_loan(params)
    assert result['detailed_payment_schedule'], "schedule missing"
    last = result['detailed_payment_schedule'][-1]
    closing_balance = parse_currency(last.get('closing_balance') or last.get('closingBalance'))
    expected_end_ltv = float((closing_balance / Decimal('200000')) * 100)
    assert result['endLTV'] == pytest.approx(expected_end_ltv)
    assert result['endLTV'] > result['startLTV']
