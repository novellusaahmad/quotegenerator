from decimal import Decimal
import pytest
from calculations import LoanCalculator

@pytest.mark.parametrize("months, days", [(6, 182), (18, 547)])
def test_bridge_retained_net_matches_input(months, days):
    calc = LoanCalculator()
    net_amount = Decimal('100000')
    annual_rate = Decimal('12')
    arrangement_fee_rate = Decimal('2')
    legal_fees = Decimal('1000')
    site_visit_fee = Decimal('500')
    title_insurance_rate = Decimal('1')

    gross = calc._calculate_gross_from_net_bridge(
        net_amount,
        annual_rate,
        months,
        'none',
        arrangement_fee_rate,
        legal_fees,
        site_visit_fee,
        title_insurance_rate,
        days,
        use_360_days=False,
    )

    fees = calc._calculate_fees(
        gross,
        arrangement_fee_rate,
        legal_fees,
        site_visit_fee,
        title_insurance_rate,
        Decimal('0'),
    )

    res = calc._calculate_bridge_retained(
        gross,
        annual_rate,
        months,
        fees,
        'simple',
        net_amount,
        days,
        use_360_days=False,
    )

    assert res['netAdvance'] == pytest.approx(float(net_amount))


def test_bridge_interest_only_net_matches_input():
    calc = LoanCalculator()
    net_amount = Decimal('90000')
    annual_rate = Decimal('12')
    loan_term = 9
    arrangement_fee_rate = Decimal('2')
    legal_fees = Decimal('1000')
    site_visit_fee = Decimal('500')
    title_insurance_rate = Decimal('1')
    loan_term_days = 274

    gross = calc._calculate_gross_from_net_bridge(
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
    )

    fees = calc._calculate_fees(
        gross,
        arrangement_fee_rate,
        legal_fees,
        site_visit_fee,
        title_insurance_rate,
        Decimal('0'),
    )

    monthly_rate = annual_rate / Decimal('12')
    res = calc._calculate_bridge_interest_only(
        gross,
        monthly_rate,
        loan_term,
        fees,
        'simple',
        net_amount,
        loan_term_days,
        use_360_days=False,
    )

    assert res['netAdvance'] == pytest.approx(float(net_amount))
