from report_utils import generate_report_schedule


def test_term_flexible_payment_schedule_includes_detail_fields():
    params = {
        'loan_type': 'term',
        'repayment_option': 'flexible_payment',
        'gross_amount': 100000,
        'annual_rate': 12,
        'loan_term': 12,
        'flexible_payment': 2000,
        'payment_frequency': 'monthly',
        'payment_timing': 'arrears',
        'start_date': '2024-01-01',
        'arrangementFee': 0,
        'totalLegalFees': 0,
    }
    schedule, _ = generate_report_schedule(params)
    first = schedule[0]
    assert 'flexible_payment_calculation' in first
    assert 'amortisation_calculation' in first
    expected_amortisation = f"{first['opening_balance']} - {first['principal_payment']} = {first['closing_balance']}"
    assert first['amortisation_calculation'] == expected_amortisation
    expected_flex = f"{first['principal_payment']} + {first['interest_amount']} = {first['total_payment']}"
    assert first['flexible_payment_calculation'] == expected_flex
    assert first['days_held'] > 0
