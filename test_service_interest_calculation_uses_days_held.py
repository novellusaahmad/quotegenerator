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

from calculations import LoanCalculator

def test_service_only_interest_calculation_uses_days_held():
    calc = LoanCalculator()
    params = {
        'loan_type': 'bridge',
        'repayment_option': 'service_only',
        'gross_amount': 2000000,
        'loan_term': 12,
        'annual_rate': 12,
        'start_date': '2015-09-30'
    }
    result = calc.calculate_bridge_loan(params)
    last = result['detailed_payment_schedule'][-1]
    days = int(last['days_held'])
    assert f"× {days}/365" in last['interest_calculation']
