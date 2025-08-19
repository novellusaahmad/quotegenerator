from decimal import Decimal
from datetime import datetime

from calculations import LoanCalculator


def _parse_currency(value: str) -> Decimal:
    return Decimal(value.replace('£', '').replace(',', ''))


def test_service_only_schedule_calendar_days():
    calc = LoanCalculator()
    calculation = {
        'gross_amount': Decimal('100000'),
        'arrangementFee': Decimal('0'),
        'totalLegalFees': Decimal('0'),
        'totalInterest': Decimal('0'),
    }
    params = {
        'repayment_option': 'service_only',
        'loan_term': 2,
        'annual_rate': Decimal('12'),
        'payment_frequency': 'monthly',
        'payment_timing': 'arrears',
        'start_date': '2024-01-01',
    }

    schedule = calc._generate_detailed_bridge_schedule(calculation, params, '£')

    interest1 = _parse_currency(schedule[0]['interest_amount'])
    interest2 = _parse_currency(schedule[1]['interest_amount'])

    expected1 = Decimal('100000') * Decimal('0.12') * Decimal('31') / Decimal('365')
    expected2 = Decimal('100000') * Decimal('0.12') * Decimal('29') / Decimal('365')

    assert abs(interest1 - expected1) < Decimal('0.01')
    assert abs(interest2 - expected2) < Decimal('0.01')
    assert interest1 != interest2

