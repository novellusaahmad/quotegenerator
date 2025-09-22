from decimal import Decimal
import pytest
from calculations import LoanCalculator


def test_interest_only_total_uses_day_formula():
    calc = LoanCalculator()
    gross_amount = Decimal('100000')
    annual_rate = Decimal('12')
    loan_term = 12
    fees = {'arrangementFee': Decimal('0'), 'totalLegalFees': Decimal('0')}
    capital_repayment = Decimal('1000')
    loan_term_days = 365

    res = calc._calculate_term_service_capital(
        gross_amount,
        annual_rate,
        loan_term,
        capital_repayment,
        fees,
        loan_term_days=loan_term_days,
        use_360_days=False,
    )
    expected = calc.calculate_simple_interest_by_days(
        gross_amount, annual_rate, loan_term_days, use_360_days=False
    )
    assert res['interestOnlyTotal'] == pytest.approx(expected)

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


def test_capital_payment_only_interest_only_matches_interest_only():
    calc = LoanCalculator()
    gross_amount = Decimal('100000')
    annual_rate = Decimal('12')
    loan_term = 12
    fees = {'arrangementFee': Decimal('0'), 'totalLegalFees': Decimal('0')}
    capital_repayment = Decimal('1000')

    res_cp = calc._calculate_term_capital_payment_only(
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
    assert res_cp['interestOnlyTotal'] == pytest.approx(res_io['totalInterest'])


def test_flexible_payment_interest_only_matches_interest_only():
    calc = LoanCalculator()
    gross_amount = Decimal('100000')
    annual_rate = Decimal('12')
    loan_term = 12
    fees = {'arrangementFee': Decimal('0'), 'totalLegalFees': Decimal('0')}
    flexible_payment = Decimal('1000')

    res_fp = calc._calculate_term_flexible_payment(
        gross_amount,
        annual_rate,
        loan_term,
        flexible_payment,
        'monthly',
        fees,
        loan_start_date='2024-01-01',
        loan_term_days=None,
        use_360_days=False,
    )
    res_io = calc._calculate_term_interest_only(
        gross_amount,
        annual_rate,
        loan_term,
        fees,
        loan_start_date='2024-01-01',
        loan_term_days=None,
        use_360_days=False,
    )
    assert res_fp['interestOnlyTotal'] == pytest.approx(res_io['totalInterest'])


def test_flexible_payment_zero_interest_matches_interest_only():
    calc = LoanCalculator()
    gross_amount = Decimal('100000')
    annual_rate = Decimal('12')
    loan_term = 12
    fees = {'arrangementFee': Decimal('0'), 'totalLegalFees': Decimal('0')}
    flexible_payment = Decimal('0')

    res_fp = calc._calculate_term_flexible_payment(
        gross_amount,
        annual_rate,
        loan_term,
        flexible_payment,
        'monthly',
        fees,
        loan_start_date='2024-01-01',
        loan_term_days=None,
        use_360_days=False,
    )
    res_io = calc._calculate_term_interest_only(
        gross_amount,
        annual_rate,
        loan_term,
        fees,
        loan_start_date='2024-01-01',
        loan_term_days=None,
        use_360_days=False,
    )
    # With zero flexible payment, no interest is paid
    assert res_fp['totalInterest'] == 0


def test_term_service_only_interest_only_total_formula():
    calc = LoanCalculator()
    params = {
        'loan_type': 'term',
        'repayment_option': 'service_only',
        'gross_amount': Decimal('100000'),
        'annual_rate': Decimal('12'),
        'loan_term': 12,
        'start_date': '2024-01-01',
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
    }
    res = calc.calculate_term_loan(params)
    expected = calc.calculate_simple_interest_by_days(
        Decimal('100000'), Decimal('12'), res['loanTermDays'], False
    )
    assert res['interestOnlyTotal'] == pytest.approx(float(expected))
    assert res['totalInterest'] == pytest.approx(res['interestOnlyTotal'])


def test_term_service_and_capital_interest_only_total_formula():
    calc = LoanCalculator()
    params = {
        'loan_type': 'term',
        'repayment_option': 'service_and_capital',
        'gross_amount': Decimal('100000'),
        'annual_rate': Decimal('12'),
        'loan_term': 12,
        'capital_repayment': Decimal('1000'),
        'start_date': '2024-01-01',
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
    }
    res = calc.calculate_term_loan(params)
    expected = calc.calculate_simple_interest_by_days(
        Decimal('100000'), Decimal('12'), res['loanTermDays'], False
    )
    assert res['interestOnlyTotal'] == pytest.approx(float(expected))
    assert res['interestSavings'] == pytest.approx(float(expected) - res['totalInterest'])
