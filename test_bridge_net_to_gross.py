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
    assert res['netAdvanceBeforeInterest'] == pytest.approx(float(net_amount))


def test_interest_only_total_interest_matches_between_paths():
    """Total interest should be the same for gross-to-net and net-to-gross paths."""
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

    res_net_to_gross = calc._calculate_bridge_interest_only(
        gross,
        monthly_rate,
        loan_term,
        fees,
        'simple',
        net_amount,
        loan_term_days,
        use_360_days=False,
    )

    res_gross_to_net = calc._calculate_bridge_interest_only(
        gross,
        monthly_rate,
        loan_term,
        fees,
        'simple',
        net_amount=None,
        loan_term_days=loan_term_days,
        use_360_days=False,
    )

    assert res_net_to_gross['totalInterest'] == pytest.approx(
        res_gross_to_net['totalInterest']
    )


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
    expected_before_interest = (
        gross_amount
        - fees['arrangementFee']
        - fees['totalLegalFees']
    )
    expected_net = expected_before_interest - first_period_interest
    assert float(result['netAdvanceBeforeInterest']) == pytest.approx(float(expected_before_interest), abs=0.01)
    assert float(result['firstPeriodInterest']) == pytest.approx(float(first_period_interest), abs=0.01)
    assert float(result['netAdvance']) == pytest.approx(float(expected_net), abs=0.01)


def test_service_and_capital_advance_net_to_gross_roundtrip():
    """Service + capital net-to-gross should invert gross-to-net when paid in advance."""
    calc = LoanCalculator()
    gross_amount = Decimal('100000')
    annual_rate = Decimal('12')
    loan_term = 9
    arrangement_fee_rate = Decimal('2')
    legal_fees = Decimal('1000')
    site_visit_fee = Decimal('500')
    title_insurance_rate = Decimal('1')
    loan_term_days = 274

    fees = calc._calculate_fees(
        gross_amount,
        arrangement_fee_rate,
        legal_fees,
        site_visit_fee,
        title_insurance_rate,
        Decimal('0'),
    )
    days_per_year = Decimal('365')
    days_first_period = Decimal(str(loan_term_days)) / Decimal(str(loan_term))
    period_interest = gross_amount * (annual_rate / Decimal('100')) * (
        days_first_period / days_per_year
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
def test_service_and_capital_net_to_gross_uses_first_period_interest(payment_frequency, payment_timing):
    """Service + capital net-to-gross retains only the first period's interest."""
    calc = LoanCalculator()
    net_amount = Decimal("100000")
    annual_rate = Decimal("12")
    loan_term = 12
    arrangement_fee_rate = Decimal("2")
    legal_fees = Decimal("1000")
    site_visit_fee = Decimal("500")
    title_insurance_rate = Decimal("1")
    start_dt = datetime.strptime("2024-01-01", "%Y-%m-%d")
    loan_term_days = (calc._add_months(start_dt, loan_term) - start_dt).days

    gross_calculated = calc._calculate_gross_from_net_bridge(
        net_amount,
        annual_rate,
        loan_term,
        "service_and_capital",
        arrangement_fee_rate,
        legal_fees,
        site_visit_fee,
        title_insurance_rate,
        loan_term_days,
        use_360_days=False,
        payment_frequency=payment_frequency,
        payment_timing=payment_timing,
        start_date=start_dt,
    )

    arrangement_decimal = arrangement_fee_rate / Decimal("100")
    title_decimal = title_insurance_rate / Decimal("100")
    fixed_fees = legal_fees + site_visit_fee
    if payment_timing == "advance":
        days_per_year = Decimal("365")
        periods = (
            Decimal("4") if payment_frequency == "quarterly" else Decimal(str(loan_term))
        )
        days_first = Decimal(str(loan_term_days)) / periods
        period_factor = (annual_rate / Decimal("100")) * (days_first / days_per_year)
    else:
        period_factor = Decimal("0")
    denominator = Decimal("1") - arrangement_decimal - title_decimal - period_factor
    expected = (net_amount + fixed_fees) / denominator

    assert float(gross_calculated) == pytest.approx(float(expected))


@pytest.mark.parametrize("payment_timing", ["advance", "arrears"])
def test_service_and_capital_net_matches_gross_schedule(payment_timing):
    calc = LoanCalculator()
    base = {
        'annual_rate': Decimal('12'),
        'loan_term': 12,
        'repayment_option': 'service_and_capital',
        'arrangement_fee_rate': Decimal('2'),
        'legal_fees': Decimal('1000'),
        'site_visit_fee': Decimal('500'),
        'title_insurance_rate': Decimal('1'),
        'capital_repayment': Decimal('1000'),
        'payment_frequency': 'monthly',
        'payment_timing': payment_timing,
        'start_date': '2024-01-01',
    }

    start_dt = datetime.strptime(base['start_date'], '%Y-%m-%d')
    loan_term_days = (calc._add_months(start_dt, base['loan_term']) - start_dt).days

    net_amount = Decimal('95000')
    gross_amount = calc._calculate_gross_from_net_bridge(
        net_amount,
        base['annual_rate'],
        base['loan_term'],
        base['repayment_option'],
        base['arrangement_fee_rate'],
        base['legal_fees'],
        base['site_visit_fee'],
        base['title_insurance_rate'],
        loan_term_days,
        use_360_days=False,
        payment_frequency=base['payment_frequency'],
        payment_timing=payment_timing,
        start_date=start_dt,
    )

    gross_params = dict(base, amount_input_type='gross', gross_amount=gross_amount)
    gross_result = calc.calculate_bridge_loan(gross_params)

    net_params = dict(base, amount_input_type='net', net_amount=net_amount)
    net_result = calc.calculate_bridge_loan(net_params)

    if payment_timing == 'arrears':
        assert gross_result['detailed_payment_schedule'] == net_result['detailed_payment_schedule']
        assert net_result['retainedInterest'] == pytest.approx(gross_result['retainedInterest'])
        assert net_result['interestRefund'] == pytest.approx(gross_result['interestRefund'])
    else:
        gross_first = gross_result['detailed_payment_schedule'][0]
        net_first = net_result['detailed_payment_schedule'][0]
        assert gross_first['interest_amount'] != net_first['interest_amount']
        assert net_first['interest_retained'] != '£0.00'
    assert net_result['totalInterest'] == pytest.approx(gross_result['totalInterest'])


@pytest.mark.parametrize(
    "payment_frequency,payment_timing",
    [
        ("monthly", "advance"),
        ("monthly", "arrears"),
        ("quarterly", "advance"),
        ("quarterly", "arrears"),
    ],
)
def test_capital_payment_only_net_to_gross_standard_formula(payment_frequency, payment_timing):
    """Capital payment only net-to-gross uses standard retained-interest formula."""
    calc = LoanCalculator()
    net_amount = Decimal("100000")
    annual_rate = Decimal("12")
    loan_term = 12
    arrangement_fee_rate = Decimal("2")
    legal_fees = Decimal("1000")
    site_visit_fee = Decimal("500")
    title_insurance_rate = Decimal("1")
    loan_term_days = 365

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

    arrangement_fee_decimal = arrangement_fee_rate / Decimal("100")
    title_insurance_decimal = title_insurance_rate / Decimal("100")
    annual_rate_decimal = annual_rate / Decimal("100")
    term_years = Decimal(str(loan_term_days)) / Decimal("365")
    interest_factor = annual_rate_decimal * term_years
    expected = (net_amount + legal_fees + site_visit_fee) / (
        Decimal("1") - arrangement_fee_decimal - title_insurance_decimal - interest_factor
    )

    assert float(gross_calculated) == pytest.approx(float(expected))


def test_service_and_capital_net_to_gross_uses_day_interest():
    """Retained interest for net advance equals Gross × Days × Daily Rate."""
    calc = LoanCalculator()
    params = {
        'annual_rate': Decimal('12'),
        'loan_term': 12,
        'repayment_option': 'service_and_capital',
        'arrangement_fee_rate': Decimal('2'),
        'legal_fees': Decimal('1000'),
        'site_visit_fee': Decimal('500'),
        'title_insurance_rate': Decimal('1'),
        'capital_repayment': Decimal('1000'),
        'payment_frequency': 'monthly',
        'payment_timing': 'advance',
        'start_date': '2024-01-01',
    }

    start_dt = datetime.strptime(params['start_date'], '%Y-%m-%d')
    loan_term_days = (calc._add_months(start_dt, params['loan_term']) - start_dt).days

    net_amount = Decimal('95000')
    gross = calc._calculate_gross_from_net_bridge(
        net_amount,
        params['annual_rate'],
        params['loan_term'],
        params['repayment_option'],
        params['arrangement_fee_rate'],
        params['legal_fees'],
        params['site_visit_fee'],
        params['title_insurance_rate'],
        loan_term_days,
        use_360_days=False,
        payment_frequency=params['payment_frequency'],
        payment_timing=params['payment_timing'],
        start_date=start_dt,
    )

    result = calc.calculate_bridge_loan(dict(params, amount_input_type='net', net_amount=net_amount))

    first = result['detailed_payment_schedule'][0]
    second = result['detailed_payment_schedule'][1]

    retained_first = Decimal(first['interest_retained'].replace('£', '').replace(',', ''))
    interest_first = Decimal(first['interest_amount'].replace('£', '').replace(',', ''))
    days_first = Decimal(str(first['days_held']))
    daily_rate = (params['annual_rate'] / Decimal('100')) / Decimal('365')
    expected = (gross * daily_rate * days_first).quantize(Decimal('0.01'))

    assert retained_first == expected
    assert interest_first == Decimal('0')
    assert Decimal(second['interest_retained'].replace('£', '').replace(',', '')) == Decimal('0')
    assert Decimal(second['interest_refund'].replace('£', '').replace(',', '')) == Decimal('0')
