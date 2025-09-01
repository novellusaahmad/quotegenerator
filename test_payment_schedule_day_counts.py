import sys, types

# Provide a minimal relativedelta stub if dateutil is missing
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
            [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
             31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]
        )
        return other.replace(year=year, month=month, day=day)
relativedelta_module.relativedelta = relativedelta
sys.modules.setdefault('dateutil', types.ModuleType('dateutil')).relativedelta = relativedelta_module
sys.modules['dateutil.relativedelta'] = relativedelta_module

from calculations import LoanCalculator


def test_payment_schedule_uses_calendar_days():
    calc = LoanCalculator()
    params = {
        'loan_type': 'bridge',
        'repayment_option': 'service_only',
        'gross_amount': 100000,
        'loan_term': 2,
        'annual_rate': 12,
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
        'payment_timing': 'arrears',
        'start_date': '2024-01-01'
    }
    result = calc.calculate_bridge_loan(params)
    schedule = result['detailed_payment_schedule']
    assert schedule[0]['days_held'] == 31
    assert schedule[1]['days_held'] == 29


def test_payment_schedule_handles_short_month_rollover():
    calc = LoanCalculator()
    params = {
        'loan_type': 'bridge',
        'repayment_option': 'service_only',
        'gross_amount': 100000,
        'loan_term': 2,
        'annual_rate': 12,
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
        'payment_timing': 'arrears',
        'start_date': '2026-01-29',
    }
    result = calc.calculate_bridge_loan(params)
    schedule = result['detailed_payment_schedule']
    assert schedule[0]['days_held'] == 31
    assert schedule[0]['end_period'] == '01/03/2026'


def test_monthly_periods_never_exceed_31_days_with_extra_term_days():
    from datetime import datetime

    calc = LoanCalculator()
    start = datetime(2024, 1, 30)
    loan_term = 1
    loan_term_days = 61
    payment_dates = calc._generate_payment_dates(start, loan_term, 'monthly', 'arrears', loan_term_days)
    ranges = calc._compute_period_ranges(start, payment_dates, loan_term, 'arrears', loan_term_days)
    assert all(r['days_held'] <= 31 for r in ranges)
