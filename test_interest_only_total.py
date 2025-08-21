from decimal import Decimal
import pytest
from calculations import LoanCalculator

def test_service_capital_interest_only_matches_service_only():
    calc = LoanCalculator()
    gross_amount = Decimal('100000')
    annual_rate = Decimal('12')
    loan_term = 12
    fees = {'arrangementFee': Decimal('0'), 'totalLegalFees': Decimal('0')}
    capital_repayment = Decimal('1000')

    res_sc = calc._calculate_term_service_capital(
        gross_amount,
        annual_rate,
        loan_term,
        capital_repayment,
        fees,
        loan_term_days=None,
        use_360_days=True,
    )
    res_io = calc._calculate_term_interest_only(
        gross_amount,
        annual_rate,
        loan_term,
        fees,
        loan_start_date='2024-01-01',
        loan_term_days=None,
        use_360_days=True,
    )
    assert res_sc['interestOnlyTotal'] == pytest.approx(res_io['totalInterest'])
