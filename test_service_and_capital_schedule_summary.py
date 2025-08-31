import sys, types
from decimal import Decimal

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
        day = min(other.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                              31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
        return other.replace(year=year, month=month, day=day)
relativedelta_module.relativedelta = relativedelta
sys.modules['dateutil'] = types.ModuleType('dateutil')
sys.modules['dateutil'].relativedelta = relativedelta_module
sys.modules['dateutil.relativedelta'] = relativedelta_module

from calculations import LoanCalculator


def _currency_to_decimal(value: str) -> Decimal:
    """Convert currency formatted string like '£1,234.56' to Decimal."""
    return Decimal(value.replace('£', '').replace(',', ''))


def _run_sac_scenario(payment_timing: str):
    """Helper to run a service-and-capital scenario for the given timing."""
    calc = LoanCalculator()
    params = {
        'loan_type': 'bridge',
        'repayment_option': 'service_and_capital',
        'gross_amount': 2000000,
        'loan_term': 12,
        'annual_rate': 12,
        'capital_repayment': 200000,
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
        'start_date': '2025-08-01',
        'property_value': 3000000,
        'payment_timing': payment_timing,
    }
    return calc.calculate_bridge_loan(params)


def _assert_summary_matches_schedule(result):
    schedule = result['detailed_payment_schedule']
    interest_total = Decimal('0')
    savings_total = Decimal('0')
    refund_total = Decimal('0')
    for r in schedule:
        accrued = Decimal(str(r.get('interest_accrued_raw', r.get('interest_amount_raw', 0))))
        retained = Decimal(str(r.get('interest_retained_raw', 0)))
        refund = Decimal(str(r.get('interest_refund_raw', 0)))
        interest_total += accrued
        if accrued == 0:
            interest_total += retained
        savings_total += Decimal(str(r.get('interest_saving_raw', 0)))
        refund_total += refund
    capital_total = sum(_currency_to_decimal(r['principal_payment']) for r in schedule)
    interest_only_total = interest_total + savings_total
    closing_balance = _currency_to_decimal(schedule[-1]['closing_balance'])

    assert interest_total.quantize(Decimal('0.01')) == Decimal(str(result['totalInterest'])).quantize(Decimal('0.01'))
    assert savings_total.quantize(Decimal('0.01')) == Decimal(str(result['interestSavings'])).quantize(Decimal('0.01'))
    assert interest_only_total.quantize(Decimal('0.01')) == Decimal(str(result['interestOnlyTotal'])).quantize(Decimal('0.01'))
    summary_interest_only = Decimal(str(result['interestOnlyTotal']))
    summary_savings = Decimal(str(result['interestSavings']))
    summary_interest = Decimal(str(result['totalInterest']))
    assert summary_interest.quantize(Decimal('0.01')) == (summary_interest_only - summary_savings).quantize(Decimal('0.01'))
    assert capital_total.quantize(Decimal('0.01')) == Decimal(str(result['gross_amount'])).quantize(Decimal('0.01'))
    assert closing_balance == Decimal('0')

    for row in schedule:
        retained = Decimal(str(row.get('interest_retained_raw', 0)))
        accrued = Decimal(str(row.get('interest_accrued_raw', row.get('interest_amount_raw', 0))))
        refund = Decimal(str(row.get('interest_refund_raw', 0)))
        saving = Decimal(str(row.get('interest_saving_raw', 0)))
        assert refund == Decimal('0') or refund == retained - accrued
        assert saving >= refund

    assert (
        refund_total.quantize(Decimal('0.01')) == Decimal('0.00')
        or refund_total.quantize(Decimal('0.01')) == savings_total.quantize(Decimal('0.01'))
    )
    assert savings_total.quantize(Decimal('0.01')) == Decimal(str(result['interestSavings'])).quantize(Decimal('0.01'))


def test_service_and_capital_summary_matches_schedule_advance():
    _assert_summary_matches_schedule(_run_sac_scenario('advance'))


def test_service_and_capital_summary_matches_schedule_arrears():
    _assert_summary_matches_schedule(_run_sac_scenario('arrears'))
