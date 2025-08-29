from decimal import Decimal
import pytest
from calculations import LoanCalculator


def test_capital_payment_only_uses_actual_days_for_savings():
    calc = LoanCalculator()
    params = {
        'loan_type': 'bridge',
        'repayment_option': 'capital_payment_only',
        'gross_amount': 2000000,
        'annual_rate': 12,
        'loan_term': 12,
        'capital_repayment': 30000,
        'arrangement_fee_rate': 2,
        'legal_fees': 3000,
        'site_visit_fee': 5000,
        'title_insurance_rate': Decimal('0.168'),
        'start_date': '2025-08-28',
        'payment_timing': 'arrears',
    }
    result = calc.calculate_bridge_loan(params)
    assert result['interestSavings'] == pytest.approx(19785.22, abs=0.01)
    assert result['totalInterest'] == pytest.approx(220214.78, abs=0.01)
