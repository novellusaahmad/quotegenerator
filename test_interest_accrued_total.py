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

from decimal import Decimal, ROUND_HALF_UP
import pytest
from calculations import LoanCalculator


def test_interest_accrued_matches_summary():
    calc = LoanCalculator()
    params = {
        'loan_type': 'bridge',
        'repayment_option': 'capital_payment_only',
        'gross_amount': 2000000,
        'loan_term': 12,
        'annual_rate': 12,
        'capital_repayment': 20000,
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
        'property_value': 3000000,
    }
    result = calc.calculate_bridge_loan(params)
    schedule = result.get('detailed_payment_schedule')
    assert schedule, 'No schedule generated'

    total_accrued = Decimal('0')
    for entry in schedule:
        amt = entry['interest_accrued'].replace('£', '').replace(',', '')
        total_accrued += Decimal(amt)
    total_accrued = total_accrued.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    summary_accrued = Decimal(str(result.get('totalInterest', 0))).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )

    retained = Decimal(str(result.get('retainedInterest'))).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )
    interest_only_total = Decimal(str(result.get('interestOnlyTotal'))).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )

    assert total_accrued == summary_accrued
    assert retained == interest_only_total
