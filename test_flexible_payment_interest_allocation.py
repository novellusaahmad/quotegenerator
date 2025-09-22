import math
from calculations import LoanCalculator

def test_flexible_payment_interest_split():
    calc = LoanCalculator()
    quote_data = {
        'loan_type': 'bridge',
        'repayment_option': 'flexible_payment',
        'gross_amount': 100000,
        'annual_rate': 12,
        'loan_term': 12,
        'flexiblePayment': 2000,
        'payment_frequency': 'monthly',
        'payment_timing': 'arrears',
        'start_date': '2024-01-01',
        'arrangementFee': 0,
        'totalLegalFees': 0,
    }
    schedule = calc.generate_payment_schedule(quote_data)
    first = schedule[0]
    expected_interest = 100000 * 0.12 * 31 / 365
    expected_principal = 2000 - expected_interest
    expected_closing = 100000 - expected_principal
    assert math.isclose(first['interest'], expected_interest, rel_tol=1e-9)
    assert math.isclose(first['principal'], expected_principal, rel_tol=1e-9)
    assert math.isclose(first['closing_balance'], expected_closing, rel_tol=1e-9)


def test_quarterly_flexible_payment_scaled_amount():
    """Ensure flexible payments are scaled for quarterly frequency"""
    calc = LoanCalculator()
    quote_data = {
        'loan_type': 'bridge',
        'repayment_option': 'flexible_payment',
        'gross_amount': 100000,
        'annual_rate': 12,
        'loan_term': 12,
        'flexiblePayment': 2000,
        'payment_frequency': 'quarterly',
        'payment_timing': 'arrears',
        'start_date': '2024-01-01',
        'arrangementFee': 0,
        'totalLegalFees': 0,
    }

    schedule = calc.generate_payment_schedule(quote_data)
    first = schedule[0]

    # Payment should be scaled to three months' worth of the flexible payment
    assert math.isclose(first['total_payment'], 6000, rel_tol=1e-9)
    # Allocation should sum to the per-payment amount
    assert math.isclose(first['interest'] + first['principal'], 6000, rel_tol=1e-9)
    # Ensure principal reduction occurred
    assert first['closing_balance'] < first['opening_balance']


def test_flexible_payment_zero_does_not_reduce_principal():
    calc = LoanCalculator()
    quote_data = {
        'loan_type': 'bridge',
        'repayment_option': 'flexible_payment',
        'gross_amount': 100000,
        'annual_rate': 12,
        'loan_term': 12,
        'flexiblePayment': 0,
        'payment_frequency': 'monthly',
        'payment_timing': 'arrears',
        'start_date': '2024-01-01',
        'arrangementFee': 0,
        'totalLegalFees': 0,
    }
    schedule = calc.generate_payment_schedule(quote_data)
    first = schedule[0]
    # With zero payment, no interest is paid and balance remains unchanged
    assert math.isclose(first['interest'], 0, rel_tol=1e-9)
    assert math.isclose(first['principal'], 0, rel_tol=1e-9)
    assert math.isclose(first['closing_balance'], 100000, rel_tol=1e-9)
