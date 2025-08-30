import pytest
from calculations import LoanCalculator

def _parse_interest(entry):
    val = entry['interest_amount']
    if isinstance(val, str):
        val = val.replace('£', '').replace(',', '')
    return float(val)

def _parse_currency(val):
    if isinstance(val, str):
        val = val.replace('£', '').replace(',', '')
    return float(val)

def test_service_and_capital_advance_has_final_interest():
    calc = LoanCalculator()
    params = {
        'repayment_option': 'service_and_capital',
        'loan_term': 12,
        'annual_rate': 12,
        'capital_repayment': 1000,
        'payment_timing': 'advance',
        'payment_frequency': 'monthly',
        'start_date': '2024-01-01',
        'loan_term_days': 366
    }
    data = {
        'gross_amount': 100000,
        'arrangementFee': 0,
        'totalLegalFees': 0,
        'totalInterest': 0
    }
    schedule = calc._generate_detailed_bridge_schedule(data, params, '£')
    assert _parse_interest(schedule[-2]) > 0
    assert _parse_interest(schedule[-1]) == pytest.approx(0, abs=0.01)

def test_capital_payment_only_advance_has_zero_final_interest():
    calc = LoanCalculator()
    params = {
        'repayment_option': 'capital_payment_only',
        'loan_term': 12,
        'annual_rate': 12,
        'capital_repayment': 1000,
        'payment_timing': 'advance',
        'payment_frequency': 'monthly',
        'start_date': '2024-01-01',
        'loan_term_days': 366
    }
    data = {
        'gross_amount': 100000,
        'arrangementFee': 0,
        'totalLegalFees': 0
    }
    schedule = calc._generate_detailed_term_schedule(data, params, '£')
    assert _parse_interest(schedule[-1]) == pytest.approx(0, abs=0.01)


def test_service_and_capital_arrears_has_final_interest():
    calc = LoanCalculator()
    params = {
        'repayment_option': 'service_and_capital',
        'loan_term': 12,
        'annual_rate': 12,
        'capital_repayment': 1000,
        'payment_timing': 'arrears',
        'payment_frequency': 'monthly',
        'start_date': '2024-01-01',
        'loan_term_days': 366
    }
    data = {
        'gross_amount': 100000,
        'arrangementFee': 0,
        'totalLegalFees': 0,
        'totalInterest': 0
    }
    schedule = calc._generate_detailed_bridge_schedule(data, params, '£')
    assert _parse_interest(schedule[-1]) > 0


def test_service_and_capital_interest_same_by_timing():
    calc = LoanCalculator()
    base_params = {
        'repayment_option': 'service_and_capital',
        'loan_term': 12,
        'annual_rate': 12,
        'capital_repayment': 1000,
        'payment_frequency': 'monthly',
        'start_date': '2024-01-01',
        'loan_term_days': 366
    }
    data = {
        'gross_amount': 100000,
        'arrangementFee': 0,
        'totalLegalFees': 0,
        'totalInterest': 0
    }
    params_adv = dict(base_params, payment_timing='advance')
    params_arr = dict(base_params, payment_timing='arrears')
    schedule_adv = calc._generate_detailed_bridge_schedule(data, params_adv, '£')
    schedule_arr = calc._generate_detailed_bridge_schedule(data, params_arr, '£')
    assert _parse_interest(schedule_arr[0]) == pytest.approx(_parse_interest(schedule_adv[0]), abs=0.01)


def test_capital_payment_only_arrears_has_zero_final_interest():
    calc = LoanCalculator()
    params = {
        'repayment_option': 'capital_payment_only',
        'loan_term': 12,
        'annual_rate': 12,
        'capital_repayment': 1000,
        'payment_timing': 'arrears',
        'payment_frequency': 'monthly',
        'start_date': '2024-01-01',
        'loan_term_days': 366
    }
    data = {
        'gross_amount': 100000,
        'arrangementFee': 0,
        'totalLegalFees': 0
    }
    schedule = calc._generate_detailed_term_schedule(data, params, '£')
    assert _parse_interest(schedule[-1]) == pytest.approx(0, abs=0.01)


def test_flexible_payment_has_final_interest():
    calc = LoanCalculator()
    params = {
        'repayment_option': 'flexible_payment',
        'loan_term': 12,
        'annual_rate': 12,
        'payment_timing': 'arrears',
        'payment_frequency': 'monthly',
        'flexible_payment': 10000,
        'start_date': '2024-01-01',
        'loan_term_days': 366
    }
    data = {
        'gross_amount': 100000,
        'arrangementFee': 0,
        'totalLegalFees': 0,
        'totalInterest': 0
    }
    schedule = calc._generate_detailed_bridge_schedule(data, params, '£')
    assert _parse_interest(schedule[-1]) > 0


def test_service_and_capital_advance_first_period_values():
    calc = LoanCalculator()
    params = {
        'repayment_option': 'service_and_capital',
        'loan_term': 12,
        'annual_rate': 12,
        'capital_repayment': 1000,
        'payment_timing': 'advance',
        'payment_frequency': 'monthly',
        'start_date': '2024-01-01',
        'loan_term_days': 366
    }
    data = {
        'gross_amount': 100000,
        'arrangementFee': 0,
        'totalLegalFees': 0,
        'totalInterest': 0
    }
    schedule = calc._generate_detailed_bridge_schedule(data, params, '£')
    first = schedule[0]
    assert _parse_currency(first['opening_balance']) == pytest.approx(100000, abs=0.1)
    expected_interest = 100000 * 0.12 * 31 / 365
    assert _parse_currency(first['interest_amount']) == pytest.approx(expected_interest, abs=0.1)
    assert _parse_currency(first['principal_payment']) == pytest.approx(1000, abs=0.1)
    assert _parse_currency(first['total_payment']) == pytest.approx(expected_interest + 1000, abs=0.1)


def test_flexible_payment_advance_first_period_values():
    calc = LoanCalculator()
    params = {
        'repayment_option': 'flexible_payment',
        'loan_term': 12,
        'annual_rate': 12,
        'payment_timing': 'advance',
        'payment_frequency': 'monthly',
        'flexible_payment': 10000,
        'start_date': '2024-01-01',
        'loan_term_days': 366
    }
    data = {
        'gross_amount': 100000,
        'arrangementFee': 0,
        'totalLegalFees': 0,
        'totalInterest': 0
    }
    schedule = calc._generate_detailed_bridge_schedule(data, params, '£')
    first = schedule[0]
    assert _parse_currency(first['opening_balance']) == pytest.approx(100000, abs=0.1)
    expected_interest = 100000 * 0.12 * 31 / 365
    assert _parse_currency(first['interest_amount']) == pytest.approx(expected_interest, abs=0.1)
    expected_principal = 10000 - expected_interest
    assert _parse_currency(first['principal_payment']) == pytest.approx(expected_principal, abs=0.1)
    assert _parse_currency(first['total_payment']) == pytest.approx(10000, abs=0.1)
