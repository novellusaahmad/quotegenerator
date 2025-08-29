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
    assert math.isclose(first['interest'], 1000.0, rel_tol=1e-9)
    assert math.isclose(first['principal'], 1000.0, rel_tol=1e-9)
    assert math.isclose(first['closing_balance'], 99000.0, rel_tol=1e-9)
