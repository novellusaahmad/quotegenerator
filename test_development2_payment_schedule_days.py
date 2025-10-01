import pytest

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


def _scenario_params(start_date: str) -> dict:
    params = _base_params(start_date)
    params.update({
        'loan_term': 24,
        'day1_advance': 356123.564,
        'net_amount': 856123.564,
        'annual_rate': 10.9865,
        'legal_fees': 0,
        'tranches': [
            {'amount': 100000, 'month': month}
            for month in range(2, 7)
        ],
    })
    return params


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


def test_development2_scenario_start_dates_align_interest_and_closing_balance():
    calc = LoanCalculator()

    scenario_one = calc.calculate_development2_loan(_scenario_params('2025-11-01'))
    scenario_two = calc.calculate_development2_loan(_scenario_params('2025-11-02'))

    total_interest_one = scenario_one['totalInterest']
    total_interest_two = scenario_two['totalInterest']

    assert total_interest_one == pytest.approx(total_interest_two, abs=1e-6)

    closing_one = float(
        scenario_one['detailed_payment_schedule'][-1]['closing_balance']
        .replace('£', '')
        .replace(',', '')
    )
    closing_two = float(
        scenario_two['detailed_payment_schedule'][-1]['closing_balance']
        .replace('£', '')
        .replace(',', '')
    )

    assert closing_one == pytest.approx(closing_two, abs=1e-9)
