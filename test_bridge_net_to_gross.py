from decimal import Decimal
from datetime import datetime
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


@pytest.mark.parametrize("months, days", [(6, 182), (18, 547)])
def test_total_net_advance_matches_input(months, days):
    """Ensure total net advance equals user net amount when using daily interest."""
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

    interest_days = calc.calculate_simple_interest_by_days(gross, annual_rate, days, False)
    total_net = gross - fees['arrangementFee'] - fees['totalLegalFees'] - interest_days
    assert float(total_net) == pytest.approx(float(net_amount))

    interest_months = gross * (annual_rate / Decimal('100')) * (Decimal(months) / Decimal('12'))
    total_net_month = gross - fees['arrangementFee'] - fees['totalLegalFees'] - interest_months
    assert float(total_net_month) != pytest.approx(float(net_amount))


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


def test_service_only_net_to_gross_roundtrip():
    """Service-only net to gross should invert gross to net when no interest is deducted."""
    calc = LoanCalculator()
    gross_amount = Decimal('100000')
    annual_rate = Decimal('12')
    loan_term = 9
    arrangement_fee_rate = Decimal('2')
    legal_fees = Decimal('1000')
    site_visit_fee = Decimal('500')
    title_insurance_rate = Decimal('1')
    loan_term_days = 274

    # Gross to net using interest-only calculation (no interest retained)
    fees = calc._calculate_fees(
        gross_amount,
        arrangement_fee_rate,
        legal_fees,
        site_visit_fee,
        title_insurance_rate,
        Decimal('0'),
    )
    monthly_rate = annual_rate / Decimal('12')
    net_result = calc._calculate_bridge_interest_only(
        gross_amount,
        monthly_rate,
        loan_term,
        fees,
        'simple',
        net_amount=None,
        loan_term_days=loan_term_days,
        use_360_days=False,
    )
    net_amount = Decimal(str(net_result['netAdvance']))

    # Net to gross should return the original gross amount
    gross_calculated = calc._calculate_gross_from_net_bridge(
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

    assert float(gross_calculated) == pytest.approx(float(gross_amount))
    # Also ensure gross-to-net removed only fees
    manual_net = gross_amount - fees['arrangementFee'] - fees['totalLegalFees']
    assert float(net_amount) == pytest.approx(float(manual_net))


def test_service_only_advance_net_to_gross_roundtrip():
    """Service-only net to gross should account for first-period interest when paid in advance."""
    calc = LoanCalculator()
    gross_amount = Decimal('100000')
    annual_rate = Decimal('12')
    loan_term = 9
    arrangement_fee_rate = Decimal('2')
    legal_fees = Decimal('1000')
    site_visit_fee = Decimal('500')
    title_insurance_rate = Decimal('1')
    loan_term_days = 274

    # Gross to net with first period interest deducted up front
    fees = calc._calculate_fees(
        gross_amount,
        arrangement_fee_rate,
        legal_fees,
        site_visit_fee,
        title_insurance_rate,
        Decimal('0'),
    )
    period_interest = calc._calculate_periodic_interest(
        gross_amount, annual_rate / Decimal('100'), 'monthly'
    )
    net_advance = gross_amount - fees['arrangementFee'] - fees['totalLegalFees'] - period_interest

    gross_calculated = calc._calculate_gross_from_net_bridge(
        net_advance,
        annual_rate,
        loan_term,
        'service_only',
        arrangement_fee_rate,
        legal_fees,
        site_visit_fee,
        title_insurance_rate,
        loan_term_days,
        use_360_days=False,
        payment_frequency='monthly',
        payment_timing='advance',
    )

    assert float(gross_calculated) == pytest.approx(float(gross_amount))


def test_service_and_capital_advance_net_deducts_interest():
    """Service + capital gross-to-net should deduct first period interest when in advance."""
    calc = LoanCalculator()
    gross_amount = Decimal('100000')
    annual_rate = Decimal('12')
    loan_term = 9
    arrangement_fee_rate = Decimal('2')
    legal_fees = Decimal('1000')
    site_visit_fee = Decimal('500')
    title_insurance_rate = Decimal('1')
    capital_repayment = Decimal('1000')
    loan_term_days = 274

    fees = calc._calculate_fees(
        gross_amount,
        arrangement_fee_rate,
        legal_fees,
        site_visit_fee,
        title_insurance_rate,
        Decimal('0'),
    )
    monthly_rate = annual_rate / Decimal('12')
    result = calc._calculate_bridge_service_capital(
        gross_amount,
        monthly_rate,
        loan_term,
        capital_repayment,
        fees,
        'simple',
        net_amount=None,
        loan_term_days=loan_term_days,
        use_360_days=False,
        payment_frequency='monthly',
        payment_timing='advance',
    )
    days_per_year = Decimal('365')
    days_per_period = Decimal(str(loan_term_days)) / Decimal(str(loan_term))
    first_period_interest = (
        gross_amount * (annual_rate / Decimal('100')) * (days_per_period / days_per_year)
    )
    expected_net = (
        gross_amount
        - fees['arrangementFee']
        - fees['totalLegalFees']
        - first_period_interest
    )
    assert float(result['netAdvance']) == pytest.approx(float(expected_net), abs=0.01)


def test_service_and_capital_advance_net_to_gross_roundtrip():
    """Service + capital net-to-gross should account for first-period interest when in advance."""
    calc = LoanCalculator()
    gross_amount = Decimal('100000')
    annual_rate = Decimal('12')
    loan_term = 9
    arrangement_fee_rate = Decimal('2')
    legal_fees = Decimal('1000')
    site_visit_fee = Decimal('500')
    title_insurance_rate = Decimal('1')
    capital_repayment = Decimal('1000')
    loan_term_days = 274

    fees = calc._calculate_fees(
        gross_amount,
        arrangement_fee_rate,
        legal_fees,
        site_visit_fee,
        title_insurance_rate,
        Decimal('0'),
    )
    period_interest = calc._calculate_periodic_interest(
        gross_amount, annual_rate / Decimal('100'), 'monthly'
    )
    net_advance = (
        gross_amount
        - fees['arrangementFee']
        - fees['totalLegalFees']
        - period_interest
    )

    gross_calculated = calc._calculate_gross_from_net_bridge(
        net_advance,
        annual_rate,
        loan_term,
        'service_and_capital',
        arrangement_fee_rate,
        legal_fees,
        site_visit_fee,
        title_insurance_rate,
        loan_term_days,
        use_360_days=False,
        payment_frequency='monthly',
        payment_timing='advance',
    )

    assert float(gross_calculated) == pytest.approx(float(gross_amount))


@pytest.mark.parametrize(
    "payment_frequency,payment_timing",
    [
        ("monthly", "advance"),
        ("monthly", "arrears"),
        ("quarterly", "advance"),
        ("quarterly", "arrears"),
    ],
)
def test_flexible_payment_net_to_gross_matches_service_only(payment_frequency, payment_timing):
    """Flexible payment net-to-gross should match the service-only formula."""
    calc = LoanCalculator()
    net_amount = Decimal("100000")
    annual_rate = Decimal("12")
    loan_term = 12
    arrangement_fee_rate = Decimal("2")
    legal_fees = Decimal("1000")
    site_visit_fee = Decimal("500")
    title_insurance_rate = Decimal("1")
    loan_term_days = 365

    gross_service = calc._calculate_gross_from_net_bridge(
        net_amount,
        annual_rate,
        loan_term,
        "service_only",
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
        "flexible_payment",
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


@pytest.mark.parametrize(
    "payment_frequency,payment_timing",
    [
        ("monthly", "advance"),
        ("monthly", "arrears"),
        ("quarterly", "advance"),
        ("quarterly", "arrears"),
    ],
)
def test_capital_payment_only_net_to_gross_matches_service_only(payment_frequency, payment_timing):
    """Capital payment only net-to-gross should match the service-only formula."""
    calc = LoanCalculator()
    net_amount = Decimal("100000")
    annual_rate = Decimal("12")
    loan_term = 12
    arrangement_fee_rate = Decimal("2")
    legal_fees = Decimal("1000")
    site_visit_fee = Decimal("500")
    title_insurance_rate = Decimal("1")
    loan_term_days = 365

    gross_service = calc._calculate_gross_from_net_bridge(
        net_amount,
        annual_rate,
        loan_term,
        "service_only",
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
        "capital_payment_only",
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
