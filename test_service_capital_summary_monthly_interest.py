import sys, types
from decimal import Decimal
import pytest

# Provide minimal stub for dateutil.relativedelta
relativedelta_module = types.ModuleType('relativedelta')
class relativedelta:  # pragma: no cover - simple stub
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


def test_service_and_capital_summary_shows_interest_and_capital():
    calc = LoanCalculator()
    params = {
        'loan_type': 'bridge',
        'repayment_option': 'service_and_capital',
        'gross_amount': 1000000,
        'annual_rate': 12,
        'loan_term': 12,
        'capital_repayment': 5000,
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
        'start_date': '2024-01-01',
    }
    result = calc.calculate_bridge_loan(params)
    expected_interest = 1000000 * 0.12 / 365 * 31
    assert result['periodicInterest'] == pytest.approx(expected_interest, abs=0.01)
    assert result['monthlyPayment'] == pytest.approx(expected_interest + 5000, abs=0.01)


def test_service_and_capital_summary_net_input_uses_gross_amount():
    calc = LoanCalculator()
    params = {
        'loan_type': 'bridge',
        'repayment_option': 'service_and_capital',
        'amount_input_type': 'net',
        'net_amount': 1000000,
        'annual_rate': 12,
        'loan_term': 12,
        'capital_repayment': 5000,
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
        'start_date': '2024-01-01',
    }
    result = calc.calculate_bridge_loan(params)
    gross = Decimal(str(result['grossAmount']))
    expected_interest = gross * Decimal('0.12') / Decimal('365') * Decimal('31')
    assert result['periodicInterest'] == pytest.approx(float(expected_interest), abs=0.01)
    assert result['monthlyPayment'] == pytest.approx(float(expected_interest) + 5000, abs=0.01)
