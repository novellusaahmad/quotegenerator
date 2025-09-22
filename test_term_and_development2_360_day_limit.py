import pytest
from calculations import LoanCalculator


def test_development2_disables_360_day_calculation():
    calc = LoanCalculator()
    params = {
        'day1_advance': 100000,
        'legal_fees': 0,
        'annual_rate': 12.0,
        'arrangement_fee_rate': 2.0,
        'title_insurance_rate': 0.01,
        'site_visit_fee': 0,
        'net_amount': 200000,
        'loan_term': 12,
        'start_date': '2025-01-01',
    }
    res_360 = calc.calculate_development2_loan({**params, 'use_360_days': True})
    res_365 = calc.calculate_development2_loan({**params, 'use_360_days': False})
    assert res_360['totalInterest'] == pytest.approx(res_365['totalInterest'])
