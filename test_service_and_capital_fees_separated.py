from decimal import Decimal
import pytest
from calculations import LoanCalculator


def _currency_to_decimal(value: str) -> Decimal:
    return Decimal(value.replace('£', '').replace(',', ''))


def test_service_and_capital_fees_separated_from_payments():
    calc = LoanCalculator()
    params = {
        'loan_type': 'bridge',
        'repayment_option': 'service_and_capital',
        'gross_amount': 100000,
        'loan_term': 12,
        'annual_rate': 12,
        'capital_repayment': 1000,
        'arrangement_fee_rate': 1,  # 1% of gross_amount = 1000
        'legal_fees': 500,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
        'payment_timing': 'arrears',
        'payment_frequency': 'monthly',
        'start_date': '2024-01-01',
    }
    result = calc.calculate_bridge_loan(params)
    schedule = calc.generate_payment_schedule(result)

    first = schedule[0]
    expected_fees = float(result['arrangementFee']) + float(result['totalLegalFees'])
    assert first.get('fees_added') == pytest.approx(expected_fees)
    assert first['total_payment'] == pytest.approx(first['interest'] + first['principal'])
    assert 'fees_added' not in schedule[1]

    detailed_schedule = calc._generate_detailed_bridge_schedule(result, params, '£')
    detailed_first = detailed_schedule[0]
    assert float(_currency_to_decimal(detailed_first['fees_added'])) == pytest.approx(expected_fees)
    total_payment = float(_currency_to_decimal(detailed_first['total_payment']))
    interest = float(_currency_to_decimal(detailed_first['interest_amount']))
    principal = float(_currency_to_decimal(detailed_first['principal_payment']))
    assert total_payment == pytest.approx(interest + principal)
    assert detailed_first['total_repayment'] == detailed_first['total_payment']
