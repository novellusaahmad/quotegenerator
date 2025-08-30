from decimal import Decimal
from calculations import LoanCalculator

def test_flexible_payment_interest_retained_and_saving():
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
        'start_date': '2024-01-01',
        'arrangement_fee': 0,
        'totalLegalFees': 0,
    }
    result = calc.calculate_bridge_loan(params)
    schedule = result['detailed_payment_schedule']
    gross = Decimal('100000')
    annual_rate = Decimal('12')
    days_per_year = Decimal('365')
    daily_rate = annual_rate / Decimal('100') / days_per_year

    first = schedule[0]
    days_first = Decimal(str(first['days_held']))
    expected_first = (gross * daily_rate * days_first).quantize(Decimal('0.01'))
    retained_first = Decimal(first['interest_retained'].replace('£', '').replace(',', ''))
    assert retained_first == expected_first

    second = schedule[1]
    days_second = Decimal(str(second['days_held']))
    expected_second = (gross * daily_rate * days_second).quantize(Decimal('0.01'))
    retained_second = Decimal(second['interest_retained'].replace('£', '').replace(',', ''))
    accrued_second = Decimal(second['interest_accrued'].replace('£', '').replace(',', ''))
    saving_second = Decimal(second['interest_saving'].replace('£', '').replace(',', ''))
    refund_second = Decimal(second['interest_refund'].replace('£', '').replace(',', ''))
    assert retained_second == expected_second
    assert saving_second == (retained_second - accrued_second).quantize(Decimal('0.01'))
    assert refund_second == (retained_second - accrued_second).quantize(Decimal('0.01'))
