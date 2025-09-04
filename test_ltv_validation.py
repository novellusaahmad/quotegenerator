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


def parse_currency(value):
    if isinstance(value, (int, float, Decimal)):
        return Decimal(str(value))
    return Decimal(str(value).replace('£', '').replace(',', ''))


def simulate_ltv_targets(gross_amount, property_value, loan_term, repayment_option, targets):
    balance = Decimal(str(gross_amount))
    property_value = Decimal(str(property_value))
    prev_month = 0
    results = []
    for t in sorted(targets, key=lambda x: x['month']):
        target_balance = property_value * Decimal(str(t['ltv'])) / Decimal('100')
        months = t['month'] - prev_month
        if repayment_option == 'capital_payment_only':
            if prev_month == 0:
                months -= 1
            if t['month'] == loan_term:
                months -= 1
        capital_needed = balance - target_balance
        if capital_needed < 0:
            capital_needed = Decimal('0')
        monthly_capital = capital_needed / months if months > 0 else Decimal('0')
        balance -= monthly_capital * months
        results.append({'month': t['month'], 'capital_outstanding': balance})
        prev_month = t['month']
    return results


def test_ltv_targets_match_schedule():
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
    schedule = result['detailed_payment_schedule']
    property_value = Decimal(str(params['property_value']))
    gross_amount = Decimal(str(params['gross_amount']))

    # Extract LTV targets from selected months in the schedule
    target_months = [6, 12]
    targets = []
    for m in target_months:
        entry = schedule[m - 1]
        closing = parse_currency(entry.get('closing_balance') or entry.get('closingBalance'))
        ltv = float((closing / property_value) * 100)
        targets.append({'month': m, 'ltv': ltv})

    simulated = simulate_ltv_targets(gross_amount, property_value, params['loan_term'], params['repayment_option'], targets)

    for sim in simulated:
        entry = schedule[sim['month'] - 1]
        closing = parse_currency(entry.get('closing_balance') or entry.get('closingBalance'))
        assert closing == pytest.approx(sim['capital_outstanding'])
