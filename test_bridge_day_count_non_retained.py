from decimal import Decimal
from calculations import LoanCalculator

def test_service_capital_uses_actual_days():
    calc = LoanCalculator()
    params = {
        'gross_amount': 100000,
        'annual_rate': 12,
        'loan_term': 1,
        'repayment_option': 'service_and_capital',
        'capital_repayment': 0,
        'start_date': '2025-01-01',
        'end_date': '2025-02-01',
    }
    result_31 = calc.calculate_bridge_loan(params)
    interest_31 = Decimal(str(result_31['totalInterest']))

    params['end_date'] = '2025-01-31'
    result_30 = calc.calculate_bridge_loan(params)
    interest_30 = Decimal(str(result_30['totalInterest']))

    assert interest_31 > interest_30
