from decimal import Decimal
import pytest
from calculations import LoanCalculator


def test_gross_to_net_and_back_fields():
    calc = LoanCalculator()
    params = {
        'amount_input_type': 'gross',
        'gross_amount': Decimal('2000000'),
        'annual_rate': Decimal('12'),
        'loan_term': 12,
        'repayment_option': 'service_and_capital',
        'capital_repayment': Decimal('10000'),
        'arrangement_fee_rate': Decimal('2'),
        'legal_fees': Decimal('1000'),
        'site_visit_fee': Decimal('1000'),
        'title_insurance_rate': Decimal('0.168'),
        'payment_frequency': 'monthly',
        'payment_timing': 'advance',
        'start_date': '2025-08-30',
    }

    gross_result = calc.calculate_bridge_loan(params)

    assert gross_result['grossAmount'] == pytest.approx(2000000.0)
    assert gross_result['netAdvance'] == pytest.approx(1934640.0)
    assert gross_result['start_date'] == '2025-08-30'
    assert gross_result['end_date'] == '2026-08-30'
    assert gross_result['loanTerm'] == 12
    assert gross_result['loanTermDays'] == 365
    assert gross_result['arrangementFee'] == pytest.approx(40000.0)
    assert gross_result['legalFees'] == pytest.approx(1000.0)
    assert gross_result['siteVisitFee'] == pytest.approx(1000.0)
    assert gross_result['titleInsurance'] == pytest.approx(3360.0)
    assert gross_result['totalInterest'] == pytest.approx(233447.68)
    assert gross_result['interestOnlyTotal'] == pytest.approx(240000.0)
    assert gross_result['periodicInterest'] == pytest.approx(20000.0)

    net_params = dict(params, amount_input_type='net', net_amount=Decimal('1934640'))
    net_result = calc.calculate_bridge_loan(net_params)

    assert net_result['grossAmount'] == pytest.approx(2000000.0)
    assert net_result['netAdvance'] == pytest.approx(1934640.0)
    assert net_result['start_date'] == '2025-08-30'
    assert net_result['end_date'] == '2026-08-30'
    assert net_result['loanTerm'] == 12
    assert net_result['loanTermDays'] == 365
    assert net_result['arrangementFee'] == pytest.approx(40000.0)
    assert net_result['legalFees'] == pytest.approx(1000.0)
    assert net_result['siteVisitFee'] == pytest.approx(1000.0)
    assert net_result['titleInsurance'] == pytest.approx(3360.0)
    assert net_result['totalInterest'] == pytest.approx(233447.68)
    assert net_result['interestOnlyTotal'] == pytest.approx(240000.0)
    assert net_result['periodicInterest'] == pytest.approx(20000.0)
