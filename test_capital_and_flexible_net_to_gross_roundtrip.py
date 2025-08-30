from decimal import Decimal
from datetime import datetime
import pytest
from calculations import LoanCalculator

@pytest.mark.parametrize("payment_frequency,payment_timing", [
    ("monthly", "advance"),
    ("monthly", "arrears"),
    ("quarterly", "advance"),
    ("quarterly", "arrears"),
])
def test_capital_payment_only_net_to_gross_roundtrip(payment_frequency, payment_timing):
    calc = LoanCalculator()
    gross_amount = Decimal('100000')
    annual_rate = Decimal('12')
    loan_term = 12
    capital_repayment = Decimal('1000')
    arrangement_fee_rate = Decimal('2')
    legal_fees = Decimal('1000')
    site_visit_fee = Decimal('500')
    title_insurance_rate = Decimal('1')
    loan_term_days = 365

    fees = calc._calculate_fees(
        gross_amount,
        arrangement_fee_rate,
        legal_fees,
        site_visit_fee,
        title_insurance_rate,
        Decimal('0'),
    )

    net = calc._calculate_bridge_capital_payment_only(
        gross_amount,
        annual_rate,
        loan_term,
        capital_repayment,
        fees,
        payment_frequency=payment_frequency,
        payment_timing=payment_timing,
    )
    net_amount = Decimal(str(net['netAdvance']))

    gross_calculated = calc._calculate_gross_from_net_bridge(
        net_amount,
        annual_rate,
        loan_term,
        'capital_payment_only',
        arrangement_fee_rate,
        legal_fees,
        site_visit_fee,
        title_insurance_rate,
        loan_term_days,
        use_360_days=False,
        payment_frequency=payment_frequency,
        payment_timing=payment_timing,
    )

    assert float(gross_calculated) == pytest.approx(float(gross_amount))


@pytest.mark.parametrize("payment_frequency,payment_timing", [
    ("monthly", "advance"),
    ("monthly", "arrears"),
    ("quarterly", "advance"),
    ("quarterly", "arrears"),
])
def test_flexible_payment_net_to_gross_roundtrip(payment_frequency, payment_timing):
    calc = LoanCalculator()
    gross_amount = Decimal('100000')
    annual_rate = Decimal('12')
    loan_term = 12
    flexible_payment = Decimal('2000')
    arrangement_fee_rate = Decimal('2')
    legal_fees = Decimal('1000')
    site_visit_fee = Decimal('500')
    title_insurance_rate = Decimal('1')
    loan_term_days = 365

    fees = calc._calculate_fees(
        gross_amount,
        arrangement_fee_rate,
        legal_fees,
        site_visit_fee,
        title_insurance_rate,
        Decimal('0'),
    )

    res = calc._calculate_bridge_flexible(
        gross_amount,
        annual_rate,
        loan_term,
        flexible_payment,
        fees,
        start_date=datetime(2024, 1, 1),
        payment_frequency=payment_frequency,
        payment_timing=payment_timing,
    )
    net_amount = Decimal(str(res['netAdvance']))

    gross_calculated = calc._calculate_gross_from_net_bridge(
        net_amount,
        annual_rate,
        loan_term,
        'flexible_payment',
        arrangement_fee_rate,
        legal_fees,
        site_visit_fee,
        title_insurance_rate,
        loan_term_days,
        use_360_days=False,
        payment_frequency=payment_frequency,
        payment_timing=payment_timing,
    )

    assert float(gross_calculated) == pytest.approx(float(gross_amount))
