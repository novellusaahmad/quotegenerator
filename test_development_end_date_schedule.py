from calculations import LoanCalculator


def test_development_schedule_respects_end_date():
    calc = LoanCalculator()
    quote = {
        'loan_type': 'development',
        'grossAmount': 100000,
        'loanTerm': 12,
        'interestRate': 12,
        'repaymentOption': 'service_only',
        'start_date': '2025-09-01',
        'end_date': '2026-05-31',
        'arrangementFee': 0,
        'totalLegalFees': 0,
        'tranches': []
    }
    schedule = calc.generate_payment_schedule(quote)
    assert len(schedule) == 9
    assert schedule[-1]['payment_date'] == '2026-05-31'
