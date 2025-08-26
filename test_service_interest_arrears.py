import pytest
from decimal import Decimal
from datetime import datetime
from calculations import LoanCalculator


def test_service_interest_arrears_total_interest():
    calc = LoanCalculator()
    gross = Decimal('100000')
    annual_rate = Decimal('12')
    start_date = datetime(2024, 1, 1)
    loan_term = 12
    loan_end = calc._add_months(start_date, loan_term)
    loan_term_days = (loan_end - start_date).days

    params = {
        'repayment_option': 'service_only',
        'loan_term': loan_term,
        'annual_rate': float(annual_rate),
        'payment_timing': 'arrears',
        'payment_frequency': 'monthly',
        'start_date': start_date.strftime('%Y-%m-%d'),
        'loan_term_days': loan_term_days,
    }

    calculation = {
        'gross_amount': float(gross),
        'arrangementFee': 0,
        'totalLegalFees': 0,
        'totalInterest': 0,
    }

    schedule = calc._generate_detailed_bridge_schedule(calculation, params, '£')
    total_interest = sum(
        float(p['interest_amount'].replace('£', '').replace(',', '')) for p in schedule
    )
    expected_interest = float(
        calc.calculate_simple_interest_by_days(gross, annual_rate, loan_term_days)
    )
    assert total_interest == pytest.approx(expected_interest, abs=0.01)
