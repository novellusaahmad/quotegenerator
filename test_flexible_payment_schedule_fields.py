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
    monthly_expected = 100000 * 0.12 / 12
    quarterly_expected = 100000 * 0.12 / 4
    assert result['monthlyInterestPayment'] == pytest.approx(monthly_expected, abs=0.01)
    assert result['quarterlyInterestPayment'] == pytest.approx(quarterly_expected, abs=0.01)
