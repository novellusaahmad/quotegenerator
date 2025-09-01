from decimal import Decimal
from report_utils import generate_report_schedule


def currency_to_decimal(val: str) -> Decimal:
    return Decimal(val.replace('£', '').replace(',', ''))


def test_interest_fields_use_days_held():
    params = {
        'loan_type': 'bridge',
        'repayment_option': 'capital_payment_only',
        'gross_amount': 100000,
        'annual_rate': 12,
        'loan_term': 12,
        'capital_repayment': 2000,
        'payment_frequency': 'monthly',
        'payment_timing': 'arrears',
        'start_date': '2024-01-01',
    }
    schedule, summary = generate_report_schedule(params)
    first = schedule[0]
    gross = Decimal('100000')
    annual_rate = Decimal('12')
    daily_rate = annual_rate / Decimal('100') / Decimal('365')
    days = Decimal(str(first['days_held']))
    expected_retained = (gross * daily_rate * days).quantize(Decimal('0.01'))
    expected_accrued = (currency_to_decimal(first['opening_balance']) * daily_rate * days).quantize(Decimal('0.01'))
    retained = currency_to_decimal(first['interest_retained'])
    accrued = currency_to_decimal(first['interest_accrued'])
    assert retained == expected_retained
    assert accrued == expected_accrued

    total_retained = sum(currency_to_decimal(r['interest_retained']) for r in schedule)
    total_refund = sum(currency_to_decimal(r['interest_refund']) for r in schedule)
    total_accrued = sum(currency_to_decimal(r['interest_accrued']) for r in schedule)
    total_saving = sum(currency_to_decimal(r['interest_saving']) for r in schedule)

    rounding = Decimal('0.01')
    expected_total_interest = (total_retained - total_refund).quantize(rounding)
    assert summary['totalInterest'] == float(expected_total_interest)
    assert summary['retainedInterest'] == float(total_retained.quantize(rounding))
    assert summary['interestRefund'] == float(total_refund.quantize(rounding))
    assert summary['total_interest_accrued'] == float(total_accrued.quantize(rounding))
    assert summary['interestSavings'] == float(total_saving.quantize(rounding))
    assert summary['monthlyInterestPayment'] == 1000.0
    assert summary['quarterlyInterestPayment'] == 3000.0
