from decimal import Decimal
import pytest
from calculations import LoanCalculator


def test_bridge_360_day_only_allowed_for_short_terms():
    calc = LoanCalculator()
    params_short = {
        'gross_amount': 100000,
        'annual_rate': 12,
        'loan_term': 12,
        'repayment_option': 'none',
        'use_360_days': True,
        'start_date': '2025-01-01',
    }
    res_short_360 = calc.calculate_bridge_loan(params_short)
    interest_short_360 = Decimal(str(res_short_360['totalInterest']))
    params_short['use_360_days'] = False
    res_short_365 = calc.calculate_bridge_loan(params_short)
    interest_short_365 = Decimal(str(res_short_365['totalInterest']))
    assert interest_short_360 > interest_short_365

    params_long = {
        'gross_amount': 100000,
        'annual_rate': 12,
        'loan_term': 13,
        'repayment_option': 'none',
        'use_360_days': True,
        'start_date': '2025-01-01',
    }
    res_long_360 = calc.calculate_bridge_loan(params_long)
    interest_long_360 = Decimal(str(res_long_360['totalInterest']))
    params_long['use_360_days'] = False
    res_long_365 = calc.calculate_bridge_loan(params_long)
    interest_long_365 = Decimal(str(res_long_365['totalInterest']))
    assert interest_long_360 == pytest.approx(interest_long_365)
