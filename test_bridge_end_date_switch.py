from calculations import LoanCalculator


def test_end_date_overrides_loan_term_schedule_length():
    calc = LoanCalculator()
    params = {
        'gross_amount': 100000,
        'annual_rate': 12,
        'loan_term': 12,
        'repayment_option': 'service_and_capital',
        'start_date': '2025-09-01',
    }
    term_result = calc.calculate_bridge_loan(params)
    assert term_result['loanTerm'] == 12
    assert len(term_result['detailed_payment_schedule']) == 12

    end_params = {
        'gross_amount': 100000,
        'annual_rate': 12,
        'loan_term': 9,
        'repayment_option': 'service_and_capital',
        'start_date': '2025-09-01',
        'end_date': '2026-05-31',
    }
    end_result = calc.calculate_bridge_loan(end_params)
    assert end_result['loanTerm'] == 9
    schedule = end_result['detailed_payment_schedule']
    assert len(schedule) == 9
    assert float(schedule[-1]['interest_amount_raw']) > 0

