import sys, types

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
        day = min(other.day, [31,29 if year %4==0 and (year%100!=0 or year%400==0) else 28,31,30,31,30,31,31,30,31,30,31][month-1])
        return other.replace(year=year, month=month, day=day)
relativedelta_module.relativedelta = relativedelta
sys.modules['dateutil'] = types.ModuleType('dateutil')
sys.modules['dateutil'].relativedelta = relativedelta_module
sys.modules['dateutil.relativedelta'] = relativedelta_module

import pytest
from calculations import LoanCalculator

@pytest.mark.parametrize("loan_type, func_name", [
    ("bridge", "calculate_bridge_loan"),
    ("term", "calculate_term_loan"),
])
@pytest.mark.parametrize("interest_type", ["simple", "compound_daily"])
def test_schedule_includes_period_fields(loan_type, func_name, interest_type):
    calc = LoanCalculator()
    params = {
        'loan_type': loan_type,
        'repayment_option': 'service_only',
        'gross_amount': 100000,
        'loan_term': 12,
        'annual_rate': 12,
        'interest_type': interest_type,
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
    }
    func = getattr(calc, func_name)
    result = func(params)
    schedule = result.get('detailed_payment_schedule')
    assert schedule, "schedule missing"
    first = schedule[0]
    assert 'start_period' in first
    assert 'end_period' in first
    assert 'days_held' in first
