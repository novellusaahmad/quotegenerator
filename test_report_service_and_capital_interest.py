from decimal import Decimal
from report_utils import generate_report_schedule
from calculations import LoanCalculator


def currency_to_decimal(val: str) -> Decimal:
    return Decimal(val.replace('£', '').replace(',', ''))


def _run_schedule(payment_timing: str):
    params = {
        'loan_type': 'bridge',
        'repayment_option': 'service_and_capital',
        'gross_amount': 100000,
        'annual_rate': 12,
        'loan_term': 12,
        'capital_repayment': 10000,
        'payment_frequency': 'monthly',
        'payment_timing': payment_timing,
        'start_date': '2024-01-01',
    }
    return generate_report_schedule(params)


def test_report_schedule_interest_fields_match_formulas():
    for timing in ['arrears', 'advance']:
        schedule, _ = _run_schedule(timing)
        first = schedule[0]
        gross = Decimal('100000')
        daily_rate = Decimal('12') / Decimal('100') / Decimal('365')
        days = Decimal(str(first['days_held']))
        capital = currency_to_decimal(first.get('capital_outstanding', first['opening_balance']))
        expected_retained = (gross * daily_rate * days).quantize(Decimal('0.01'))
        expected_accrued = (capital * daily_rate * days).quantize(Decimal('0.01'))
        expected_refund = (expected_retained - expected_accrued).quantize(Decimal('0.01'))
        assert currency_to_decimal(first['interest_retained']) == expected_retained
        assert currency_to_decimal(first['interest_accrued']) == expected_accrued
        assert currency_to_decimal(first['interest_refund']) == expected_refund
        assert currency_to_decimal(first['interest_saving']) == expected_refund


def test_report_schedule_net_input_has_no_retained_interest():
    params = {
        'loan_type': 'bridge',
        'repayment_option': 'service_and_capital',
        'amount_input_type': 'net',
        'net_amount': 1000000,
        'annual_rate': 12,
        'loan_term': 12,
        'capital_repayment': 5000,
        'payment_frequency': 'monthly',
        'payment_timing': 'arrears',
        'start_date': '2024-01-01',
    }
    schedule, summary = generate_report_schedule(params)
    for row in schedule:
        assert row['interest_retained'] == '£0.00'
        assert row['interest_refund'] == '£0.00'
    assert 'retainedInterest' not in summary
    assert 'interestRefund' not in summary

    calc = LoanCalculator()
    calc_result = calc.calculate_bridge_loan(params)
    gross = Decimal(str(calc_result.get('gross_amount', calc_result.get('grossAmount'))))
    term_days = calc_result.get('loanTermDays')
    rate = Decimal(str(calc_result.get('interestRate', params.get('annual_rate'))))
    expected_io = calc.calculate_simple_interest_by_days(gross, rate, term_days, False)
    total_interest = Decimal(str(summary['totalInterest']))
    expected_savings = expected_io - total_interest
    assert Decimal(str(summary['interestOnlyTotal'])).quantize(Decimal('0.01')) == expected_io.quantize(Decimal('0.01'))
    assert Decimal(str(summary['interestSavings'])).quantize(Decimal('0.01')) == expected_savings.quantize(Decimal('0.01'))
