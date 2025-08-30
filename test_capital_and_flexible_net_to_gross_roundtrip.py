from decimal import Decimal
import pytest
from calculations import LoanCalculator

@pytest.mark.parametrize("repayment_option", [
    "service_and_capital",
    "capital_payment_only",
    "flexible_payment",
])
@pytest.mark.parametrize("payment_frequency,payment_timing", [
    ("monthly", "advance"),
    ("monthly", "arrears"),
    ("quarterly", "advance"),
    ("quarterly", "arrears"),
])
def test_net_to_gross_matches_service_only(repayment_option, payment_frequency, payment_timing):
    calc = LoanCalculator()
    net_amount = Decimal('100000')
    annual_rate = Decimal('12')
    loan_term = 12
    arrangement_fee_rate = Decimal('2')
    legal_fees = Decimal('1000')
    site_visit_fee = Decimal('500')
    title_insurance_rate = Decimal('1')
    loan_term_days = 365

    gross_service = calc._calculate_gross_from_net_bridge(
        net_amount,
        annual_rate,
        loan_term,
        'service_only',
        arrangement_fee_rate,
        legal_fees,
        site_visit_fee,
        title_insurance_rate,
        loan_term_days,
        use_360_days=False,
        payment_frequency=payment_frequency,
        payment_timing=payment_timing,
    )

    gross_calculated = calc._calculate_gross_from_net_bridge(
        net_amount,
        annual_rate,
        loan_term,
        repayment_option,
        arrangement_fee_rate,
        legal_fees,
        site_visit_fee,
        title_insurance_rate,
        loan_term_days,
        use_360_days=False,
        payment_frequency=payment_frequency,
        payment_timing=payment_timing,
    )

    assert float(gross_calculated) == pytest.approx(float(gross_service))
