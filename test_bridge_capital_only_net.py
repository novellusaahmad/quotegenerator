from decimal import Decimal
import pytest
from calculations import LoanCalculator


def test_bridge_capital_only_net_uses_standard_formula():
    calc = LoanCalculator()
    net_amount = Decimal('95000')
    annual_rate = Decimal('12')
    loan_term = 12
    arrangement_fee_rate = Decimal('2')
    legal_fees = Decimal('1000')
    site_visit_fee = Decimal('500')
    title_insurance_rate = Decimal('1')
    loan_term_days = 365

    gross = calc._calculate_gross_from_net_bridge(
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
        payment_frequency='monthly',
        payment_timing='advance',
    )

    arrangement_fee_decimal = arrangement_fee_rate / Decimal('100')
    title_insurance_decimal = title_insurance_rate / Decimal('100')
    annual_rate_decimal = annual_rate / Decimal('100')
    term_years = Decimal(str(loan_term_days)) / Decimal('365')
    interest_factor = annual_rate_decimal * term_years
    expected = (net_amount + legal_fees + site_visit_fee) / (
        Decimal('1') - arrangement_fee_decimal - title_insurance_decimal - interest_factor
    )

    assert float(gross) == pytest.approx(float(expected))
