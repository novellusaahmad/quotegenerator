from calculations import LoanCalculator
from datetime import datetime

def test_end_date_before_start_adjusts():
    calc = LoanCalculator()
    params = {
        'gross_amount': 100000,
        'annual_rate': 12,
        'loan_term': 12,
        'repayment_option': 'service_and_capital',
        'start_date': '2025-09-01',
        'end_date': '2025-08-01'
    }
    res = calc.calculate_bridge_loan(params)
    assert res['loanTerm'] == 1
    assert res['loanTermDays'] == 1
    assert res['end_date'] == '2025-09-01'


def test_zero_loan_term_defaults_to_one():
    calc = LoanCalculator()
    params = {
        'gross_amount': 100000,
        'annual_rate': 12,
        'loan_term': 0,
        'repayment_option': 'service_and_capital',
        'start_date': '2025-09-01'
    }
    res = calc.calculate_bridge_loan(params)
    assert res['loanTerm'] == 1
    start = datetime.strptime('2025-09-01', '%Y-%m-%d')
    end = datetime.strptime(res['end_date'], '%Y-%m-%d')
    assert (end - start).days + 1 == res['loanTermDays'] == 30
