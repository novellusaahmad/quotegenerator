from calculations import LoanCalculator


def _base_params(start_date: str) -> dict:
    return {
        'loan_type': 'development2',
        'start_date': start_date,
        'loan_term': 18,
        'day1_advance': 100000,
        'net_amount': 800000,
        'annual_rate': 12.0,
        'legal_fees': 7587.94,
        'arrangement_fee_rate': 0,
        'title_insurance_rate': 0,
        'site_visit_fee': 0,
        'tranches': [],
    }


def test_development2_first_period_for_start_on_first_matches_excel_days():
    calc = LoanCalculator()
    result = calc.calculate_development2_loan(_base_params('2025-11-01'))
    schedule = result['detailed_payment_schedule']
    first_period = schedule[0]

    assert first_period['days'] == 30
    assert first_period['payment_date'].endswith('30/11/2025')
    assert '^30' in first_period['interest_calculation']


def test_development2_first_period_for_january_start_spans_full_month():
    calc = LoanCalculator()
    result = calc.calculate_development2_loan(_base_params('2025-01-01'))
    schedule = result['detailed_payment_schedule']
    first_period = schedule[0]

    assert first_period['days'] == 31
    assert first_period['payment_date'].endswith('31/01/2025')
    assert '^31' in first_period['interest_calculation']


def test_development2_first_period_for_end_of_month_start_dates_match_excel_days():
    calc = LoanCalculator()

    scenarios = [
        ('2025-11-29', '28/12/2025', 30),
        ('2025-11-30', '29/12/2025', 30),
        ('2025-01-31', '28/02/2025', 29),
    ]

    for start_date, expected_end, expected_days in scenarios:
        result = calc.calculate_development2_loan(_base_params(start_date))
        schedule = result['detailed_payment_schedule']
        first_period = schedule[0]

        assert first_period['days'] == expected_days
        assert first_period['payment_date'].endswith(expected_end)
        assert f'^{expected_days}' in first_period['interest_calculation']
