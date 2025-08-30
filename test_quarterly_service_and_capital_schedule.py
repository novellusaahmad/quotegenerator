import sys, types
from calculations import LoanCalculator

# Provide minimal stub for dateutil.relativedelta to avoid external dependency
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


def test_quarterly_service_and_capital_schedule_groups_months():
    calc = LoanCalculator()
    params = {
        'loan_type': 'bridge',
        'repayment_option': 'service_and_capital',
        'gross_amount': 100000,
        'annual_rate': 12,
        'loan_term': 12,
        'capital_repayment': 1000,
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
        'start_date': '2024-01-01',
        'payment_frequency': 'quarterly',
        'payment_timing': 'advance',
    }
    result = calc.calculate_bridge_loan(params)
    schedule = result['detailed_payment_schedule']

    assert len(schedule) == 5
    first = schedule[0]
    assert first['start_period'] == '01/01/2024'
    assert first['end_period'] == '01/04/2024'
    assert first['days_held'] == 91
