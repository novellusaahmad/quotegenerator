from decimal import Decimal
from calculations import LoanCalculator

def test_term_capital_payment_only_uses_actual_days():
    calc = LoanCalculator()
    params = {
        'gross_amount': 100000,
        'annual_rate': 12,
        'loan_term': 3,
        'repayment_option': 'capital_payment_only',
        'capital_repayment': 0,
        'start_date': '2025-01-01',
        'payment_frequency': 'monthly',
        'payment_timing': 'advance',
    }
    calculation = {'grossAmount': 100000, 'arrangementFee': 0, 'totalLegalFees': 0}
    schedule = calc._generate_detailed_term_schedule(calculation, params, '£')
    int1 = Decimal(schedule[0]['interest_amount'].replace('£', '').replace(',', ''))
    int2 = Decimal(schedule[1]['interest_amount'].replace('£', '').replace(',', ''))
    expected1 = calc.calculate_simple_interest_by_days(Decimal('100000'), Decimal('12'), 31, False)
    expected2 = calc.calculate_simple_interest_by_days(Decimal('100000'), Decimal('12'), 28, False)
    assert abs(int1 - expected1) < Decimal('0.01')
    assert abs(int2 - expected2) < Decimal('0.01')
    assert int1 > int2
