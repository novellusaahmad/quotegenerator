from calculations import LoanCalculator


def test_development_net_to_gross_day_count():
    calc = LoanCalculator()
    params = {
        'net_amount': 100000,
        'loan_term': 12,
        'annual_rate': 12,
        'start_date': '2025-09-01',
        'day1_advance': 100000,
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
        'tranches': [],
    }
    result = calc.calculate_development_loan(params)
    first = result['detailed_payment_schedule'][0]
    assert first['days_held'] == 30
    exponent = int(first['interest_calculation'].split('^')[1])
    assert exponent == 30
