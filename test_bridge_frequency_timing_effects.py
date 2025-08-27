import pytest
from calculations import LoanCalculator


def test_service_and_capital_frequency_changes_totals():
    calc = LoanCalculator()
    base = {
        'loan_type': 'bridge',
        'repayment_option': 'service_and_capital',
        'gross_amount': 100000,
        'annual_rate': 12,
        'loan_term': 12,
        'capital_repayment': 1000,
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
        'start_date': '2024-01-01',
    }
    params_monthly = base.copy()
    params_monthly['payment_frequency'] = 'monthly'
    params_monthly['payment_timing'] = 'arrears'
    params_quarterly = base.copy()
    params_quarterly['payment_frequency'] = 'quarterly'
    params_quarterly['payment_timing'] = 'arrears'
    res_month = calc.calculate_bridge_loan(params_monthly)
    res_quarter = calc.calculate_bridge_loan(params_quarterly)
    assert res_month['totalInterest'] != pytest.approx(res_quarter['totalInterest'])
    assert len(res_month['payment_schedule']) != len(res_quarter['payment_schedule'])


def test_capital_payment_only_timing_changes_totals():
    calc = LoanCalculator()
    base = {
        'loan_type': 'bridge',
        'repayment_option': 'capital_payment_only',
        'gross_amount': 100000,
        'annual_rate': 12,
        'loan_term': 12,
        'capital_repayment': 1000,
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
        'start_date': '2024-01-01',
    }
    params_adv = base.copy()
    params_adv['payment_timing'] = 'advance'
    params_adv['payment_frequency'] = 'monthly'
    params_arr = base.copy()
    params_arr['payment_timing'] = 'arrears'
    params_arr['payment_frequency'] = 'monthly'
    res_adv = calc.calculate_bridge_loan(params_adv)
    res_arr = calc.calculate_bridge_loan(params_arr)
    assert res_adv['totalInterest'] != pytest.approx(res_arr['totalInterest'])
