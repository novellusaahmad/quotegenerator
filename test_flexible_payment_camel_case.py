import report_utils  # registers dateutil stub
from calculations import LoanCalculator


def test_flexible_payment_camel_case():
    calc = LoanCalculator()
    params = {
        'gross_amount': 100000,
        'annual_rate': 12,
        'loan_term': 12,
        'repayment_option': 'flexible_payment',
        'flexiblePayment': 30000,
        'payment_frequency': 'monthly',
        'payment_timing': 'arrears',
    }
    result = calc.calculate_bridge_loan(params)
    assert result['monthlyPayment'] == 30000.0
    first = result['detailed_payment_schedule'][0]
    assert first['interest_amount'] == '£1,000.00'
    assert first['principal_payment'] == '£29,000.00'
