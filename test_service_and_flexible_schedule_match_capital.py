from report_utils import generate_report_schedule


def test_service_and_capital_matches_capital_payment_schedule():
    base = {
        'gross_amount': 100000,
        'annual_rate': 12,
        'loan_term': 12,
        'payment_frequency': 'monthly',
        'payment_timing': 'arrears',
        'start_date': '2024-01-01',
    }
    params_capital = dict(base, repayment_option='capital_payment_only', capital_repayment=2000)
    params_service = dict(base, repayment_option='service_and_capital', capital_repayment=2000)
    capital_schedule = generate_report_schedule(params_capital)
    service_schedule = generate_report_schedule(params_service)
    assert service_schedule == capital_schedule


def test_flexible_payment_matches_capital_payment_schedule():
    base = {
        'gross_amount': 100000,
        'annual_rate': 12,
        'loan_term': 12,
        'payment_frequency': 'monthly',
        'payment_timing': 'arrears',
        'start_date': '2024-01-01',
    }
    params_capital = dict(base, repayment_option='capital_payment_only', capital_repayment=2000)
    params_flex = dict(base, repayment_option='flexible_payment', flexible_payment=2000)
    capital_schedule = generate_report_schedule(params_capital)
    flex_schedule = generate_report_schedule(params_flex)
    assert flex_schedule != capital_schedule
    assert 'amortisation_calculation' in flex_schedule[0]


def test_flexible_payment_camel_case_matches_capital_payment_schedule():
    base = {
        'gross_amount': 100000,
        'annual_rate': 12,
        'loan_term': 12,
        'payment_frequency': 'monthly',
        'payment_timing': 'arrears',
        'start_date': '2024-01-01',
    }
    params_capital = dict(base, repayment_option='capital_payment_only', capital_repayment=2000)
    params_flex = dict(base, repayment_option='flexible_payment', flexiblePayment=2000)
    capital_schedule = generate_report_schedule(params_capital)
    flex_schedule = generate_report_schedule(params_flex)
    assert flex_schedule != capital_schedule
    assert 'amortisation_calculation' in flex_schedule[0]


def test_schedule_field_sets_match_capital_format():
    base = {
        'gross_amount': 100000,
        'annual_rate': 12,
        'loan_term': 12,
        'payment_frequency': 'monthly',
        'payment_timing': 'arrears',
        'start_date': '2024-01-01',
    }
    params_capital = dict(base, repayment_option='capital_payment_only', capital_repayment=2000)
    params_service = dict(base, repayment_option='service_and_capital', capital_repayment=2000)
    params_flex = dict(base, repayment_option='flexible_payment', flexible_payment=2000)
    cap = generate_report_schedule(params_capital)
    svc = generate_report_schedule(params_service)
    flex = generate_report_schedule(params_flex)
    cap_fields = set(cap[0].keys())
    assert set(svc[0].keys()) == cap_fields
    expected_flex_fields = {
        'payment_date', 'start_period', 'end_period', 'days_held',
        'opening_balance', 'tranche_release', 'interest_calculation',
        'interest_amount', 'interest_saving', 'principal_payment',
        'total_payment', 'closing_balance', 'balance_change',
        'flexible_payment_calculation', 'amortisation_calculation'
    }
    assert set(flex[0].keys()) == expected_flex_fields

