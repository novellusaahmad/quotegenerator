import sys
import types
import pytest

# Provide minimal stub for dateutil.relativedelta to avoid external dependency
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
            [
                31,
                29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                31,
                30,
                31,
                30,
                31,
                31,
                30,
                31,
                30,
                31,
            ][month - 1],
        )
        return other.replace(year=year, month=month, day=day)


relativedelta_module.relativedelta = relativedelta
sys.modules['dateutil'] = types.ModuleType('dateutil')
sys.modules['dateutil'].relativedelta = relativedelta_module
sys.modules['dateutil.relativedelta'] = relativedelta_module

from report_utils import generate_report_schedule


def test_report_service_only_includes_reference_interest_payments():
    params = {
        'loan_type': 'bridge',
        'repayment_option': 'service_only',
        'gross_amount': 100000,
        'annual_rate': 12,
        'loan_term': 12,
        'payment_frequency': 'monthly',
        'payment_timing': 'arrears',
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
        'start_date': '2024-01-01',
    }
    _, summary = generate_report_schedule(params)
    assert summary['monthlyInterestPayment'] == pytest.approx(100000 * 0.12 / 12, abs=0.01)
    assert summary['quarterlyInterestPayment'] == pytest.approx(100000 * 0.12 / 4, abs=0.01)

