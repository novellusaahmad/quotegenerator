import sys, types
import pytest

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


def test_capital_only_schedule_fields_present():
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
    required_fields = [
        'start_period', 'end_period', 'days_held',
        'capital_outstanding', 'annual_interest_rate', 'interest_pa',
        'scheduled_repayment', 'interest_accrued', 'interest_retained',
        'interest_refund', 'running_ltv'
    ]
    for idx, entry in enumerate(schedule, start=1):
        for field in required_fields:
            assert field in entry, f"Missing field {field} in period {idx}"
    assert schedule[-1].get('interest_refund') not in (None, ''), 'Interest refund missing in last period'
    assert result['monthlyInterestPayment'] == pytest.approx(2000000 * 0.12 / 12, abs=0.01)
    assert result['quarterlyInterestPayment'] == pytest.approx(2000000 * 0.12 / 4, abs=0.01)
