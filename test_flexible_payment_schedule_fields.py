from calculations import LoanCalculator
import pytest

def test_flexible_payment_schedule_fields_present():
    calc = LoanCalculator()
    params = {
        'loan_type': 'bridge',
        'repayment_option': 'flexible_payment',
        'gross_amount': 100000,
        'annual_rate': 12,
        'loan_term': 12,
        'flexible_payment': 2000,
        'payment_frequency': 'monthly',
        'payment_timing': 'arrears',
        'arrangement_fee_rate': 0,
        'legal_fees': 0,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
        'property_value': 150000,
    }
    result = calc.calculate_bridge_loan(params)
    schedule = result.get('detailed_payment_schedule')
    assert schedule, 'No schedule generated'
    required_fields = [
        'start_period', 'end_period', 'days_held',
        'capital_outstanding', 'annual_interest_rate', 'interest_pa',
        'scheduled_repayment', 'interest_accrued', 'interest_retained',
        'interest_refund', 'running_ltv'
    ]
    for idx, entry in enumerate(schedule, start=1):
        for field in required_fields:
            assert field in entry, f"Missing field {field} in period {idx}"
    daily_rate = 0.12 / 365
    days_first = schedule[0]['days_held']
    days_quarter = sum(p['days_held'] for p in schedule[:3])
    assert result['monthlyInterestPayment'] == pytest.approx(100000 * daily_rate * days_first, abs=0.01)
    assert result['quarterlyInterestPayment'] == pytest.approx(100000 * daily_rate * days_quarter, abs=0.01)
