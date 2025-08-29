from report_utils import generate_report_schedule


def test_service_and_capital_matches_capital_payment_schedule():
    base = {
        'gross_amount': 100000,
        'annual_rate': 12,
        'loan_term': 12,
        'payment_frequency': 'monthly',
        'payment_timing': 'arrears',
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
    }
    params_capital = dict(base, repayment_option='capital_payment_only', capital_repayment=2000)
    params_flex = dict(base, repayment_option='flexible_payment', flexible_payment=2000)
    capital_schedule = generate_report_schedule(params_capital)
    flex_schedule = generate_report_schedule(params_flex)
    assert flex_schedule == capital_schedule
