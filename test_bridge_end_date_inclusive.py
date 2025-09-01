from calculations import LoanCalculator


def test_bridge_end_date_includes_final_day():
    calc = LoanCalculator()
    params = {
        'gross_amount': 100000,
        'annual_rate': 12,
        'loan_term': 9,
        'repayment_option': 'service_and_capital',
        'start_date': '2025-09-01',
        'end_date': '2026-05-31',
    }
    result = calc.calculate_bridge_loan(params)
    assert result['loanTermDays'] == 273

