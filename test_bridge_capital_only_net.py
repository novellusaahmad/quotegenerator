from decimal import Decimal
import pytest
from calculations import LoanCalculator


def test_bridge_capital_only_net_matches_input():
    calc = LoanCalculator()
    net_amount = Decimal('95000')
    annual_rate = Decimal('12')
    loan_term = 12
    arrangement_fee_rate = Decimal('2')
    legal_fees = Decimal('1000')
    site_visit_fee = Decimal('500')
    title_insurance_rate = Decimal('1')
    loan_term_days = 365
    capital_repayment = Decimal('1000')

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

    fees = calc._calculate_fees(
        gross,
        arrangement_fee_rate,
        legal_fees,
        site_visit_fee,
        title_insurance_rate,
        Decimal('0'),
    )

    res = calc._calculate_bridge_capital_only(
        gross,
        annual_rate,
        loan_term,
        capital_repayment,
        fees,
    )

    assert res['netAdvance'] == pytest.approx(float(net_amount))
