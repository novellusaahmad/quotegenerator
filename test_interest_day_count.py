from decimal import Decimal
from datetime import datetime
import pytest
from calculations import LoanCalculator


def test_calendar_day_count_matches_manual_days():
    calc = LoanCalculator()
    principal = Decimal('100000')
    rate = Decimal('12')
    start = datetime(2024, 1, 1)
    # Interest using calendar day count for 15 months from Jan 1 2024
    interest_calendar = calc.calculate_interest_amount(
        principal, rate, interest_type='simple', start_date=start, term_months=15
    )
    # Interest using month-based year fraction (15 months -> 1.25 years)
    interest_years = calc.calculate_interest_amount(
        principal, rate, Decimal('15') / Decimal('12'), 'simple'
    )
    expected = principal * (rate / Decimal('100')) * Decimal('456') / Decimal('365')
    assert abs(interest_calendar - expected) < Decimal('0.01')
    assert interest_years > interest_calendar


def test_calendar_day_count_respects_start_year():
    calc = LoanCalculator()
    principal = Decimal('100000')
    rate = Decimal('12')
    interest_leap = calc.calculate_interest_amount(
        principal, rate, interest_type='simple', start_date=datetime(2024, 1, 1), term_months=15
    )
    interest_non_leap = calc.calculate_interest_amount(
        principal, rate, interest_type='simple', start_date=datetime(2025, 1, 1), term_months=15
    )
    assert interest_leap > interest_non_leap
