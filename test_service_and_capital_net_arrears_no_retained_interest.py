import sys, types
from decimal import Decimal
from datetime import datetime
import pytest
from calculations import LoanCalculator

# Minimal stub for dateutil.relativedelta to avoid external dependency
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


def _currency_to_decimal(value: str) -> Decimal:
    return Decimal(value.replace('£', '').replace(',', ''))


def test_net_arrears_has_no_retained_interest():
    calc = LoanCalculator()
    start_date = datetime(2024, 1, 1)
    loan_term = 12
    loan_end = calc._add_months(start_date, loan_term)
    loan_term_days = (loan_end - start_date).days
    params = {
        'loan_type': 'bridge',
        'repayment_option': 'service_and_capital',
        'amount_input_type': 'net',
        'net_amount': 1000000,
        'annual_rate': 12,
        'loan_term': loan_term,
        'capital_repayment': 5000,
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'loan_term_days': loan_term_days,
        'payment_timing': 'arrears',
        'payment_frequency': 'monthly',
    }
    result = calc.calculate_bridge_loan(params)
    schedule = result['detailed_payment_schedule']

    for row in schedule:
        assert row['interest_retained'] == '£0.00'
        assert row['interest_refund'] == '£0.00'

    total_interest = sum(_currency_to_decimal(r['interest_accrued']) for r in schedule)
    total_capital = sum(_currency_to_decimal(r['principal_payment']) for r in schedule)

    assert total_interest.quantize(Decimal('0.01')) == Decimal(str(result['totalInterest'])).quantize(Decimal('0.01'))
    gross = Decimal(str(result.get('gross_amount', result.get('grossAmount'))))
    assert total_capital.quantize(Decimal('0.01')) == gross.quantize(Decimal('0.01'))
    assert Decimal(str(result.get('retainedInterest', 0))) == Decimal('0')
    assert Decimal(str(result.get('interestRefund', 0))) == Decimal('0')
    assert Decimal(str(result['interestSavings'])) == Decimal('0')
