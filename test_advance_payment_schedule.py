import pytest
from calculations import LoanCalculator

def _parse_interest(entry):
    val = entry['interest_amount']
    if isinstance(val, str):
        val = val.replace('£', '').replace(',', '')
    return float(val)

def test_service_and_capital_advance_has_zero_final_interest():
    calc = LoanCalculator()
    params = {
        'repayment_option': 'service_and_capital',
        'loan_term': 12,
        'annual_rate': 12,
        'capital_repayment': 1000,
        'payment_timing': 'advance',
        'payment_frequency': 'monthly',
        'start_date': '2024-01-01'
    }
    data = {
        'gross_amount': 100000,
        'arrangementFee': 0,
        'totalLegalFees': 0,
        'totalInterest': 0
    }
    schedule = calc._generate_detailed_bridge_schedule(data, params, '£')
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
        'start_date': '2024-01-01'
    }
    data = {
        'gross_amount': 100000,
        'arrangementFee': 0,
        'totalLegalFees': 0
    }
    schedule = calc._generate_detailed_term_schedule(data, params, '£')
    assert _parse_interest(schedule[-1]) == pytest.approx(0, abs=0.01)
