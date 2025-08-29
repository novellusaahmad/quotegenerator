from decimal import Decimal
import sys, types

# Minimal relativedelta stub (to avoid dependency on python-dateutil)
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
            [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][
                month - 1
            ],
        )
        return other.replace(year=year, month=month, day=day)

relativedelta_module.relativedelta = relativedelta
sys.modules['dateutil'] = types.ModuleType('dateutil')
sys.modules['dateutil'].relativedelta = relativedelta_module
sys.modules['dateutil.relativedelta'] = relativedelta_module

from calculations import LoanCalculator


def test_interest_retained_split_monthly():
    calc = LoanCalculator()
    params = {
        'loan_type': 'bridge',
        'repayment_option': 'capital_payment_only',
        'gross_amount': 2000000,
        'loan_term': 12,
        'annual_rate': 7,
        'capital_repayment': 20000,
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
        'property_value': 3000000,
    }
    result = calc.calculate_bridge_loan(params)
    schedule = result['detailed_payment_schedule']
    retained_total = Decimal(str(result['retainedInterest']))
    periods = len(schedule)
    first_period_retained = Decimal(schedule[0]['interest_retained'].replace('£', '').replace(',', ''))
    # Expect first period retained to be roughly total/periods
    expected = retained_total / periods
    assert abs(first_period_retained - expected) < Decimal('0.01')
    # Ensure total retained across schedule equals retainedInterest
    total_split = sum(Decimal(entry['interest_retained'].replace('£', '').replace(',', '')) for entry in schedule)
    assert abs(total_split - retained_total) < Decimal('0.05')
