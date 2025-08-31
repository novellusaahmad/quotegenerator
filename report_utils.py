"""Utility helpers for payment schedule generation used in reports."""

from typing import Any, Dict, List, Tuple

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

from calculations import LoanCalculator


# Provide a minimal fallback for ``dateutil.relativedelta`` so that schedule
# generation can run in environments where the optional dependency is missing
# (such as the execution sandbox used for the tests).  Only the behaviour
# needed by the loan calculator is implemented – addition of whole months.
try:  # pragma: no cover - prefer the real library when available
    from dateutil.relativedelta import relativedelta as _relativedelta  # type: ignore
except Exception:  # pragma: no cover
    import sys
    import types
    from datetime import datetime

    class _relativedelta:  # minimal replacement
        def __init__(self, months: int = 0):
            self.months = months

        # ``datetime + relativedelta(months=n)`` is used in the calculator.  We
        # implement the right-hand addition protocol so this class behaves the
        # same for that use case.
        def __radd__(self, other: datetime) -> datetime:
            month = other.month - 1 + self.months
            year = other.year + month // 12
            month = month % 12 + 1
            # Clamp the day to the last valid day of the target month.
            month_lengths = [31, 29 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 28,
                             31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            day = min(other.day, month_lengths[month - 1])
            return other.replace(year=year, month=month, day=day)

    # Register the stub so ``from dateutil.relativedelta import relativedelta``
    # works inside the calculator.
    stub_module = types.ModuleType("relativedelta")
    stub_module.relativedelta = _relativedelta
    dateutil_module = sys.modules.setdefault("dateutil", types.ModuleType("dateutil"))
    dateutil_module.relativedelta = stub_module
    sys.modules["dateutil.relativedelta"] = stub_module

    relativedelta = _relativedelta
else:  # pragma: no cover
    relativedelta = _relativedelta


def _to_decimal(value: Any, currency_symbol: str) -> Decimal:
    """Convert a currency string or numeric value to ``Decimal``."""
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    if isinstance(value, str):
        return Decimal(value.replace(currency_symbol, '').replace(',', ''))
    return Decimal(str(value))


def recalculate_summary(schedule: List[Dict[str, Any]]) -> Dict[str, float]:
    """Aggregate interest values from a detailed schedule."""
    if not schedule:
        return {}

    currency_symbol = schedule[0].get('opening_balance', '£')[0]
    total_interest_amt = Decimal('0')
    total_savings = Decimal('0')
    total_retained = Decimal('0')
    total_refund = Decimal('0')
    total_accrued = Decimal('0')

    for entry in schedule:
        total_interest_amt += _to_decimal(entry.get('interest_amount', 0), currency_symbol)
        total_savings += _to_decimal(entry.get('interest_saving', 0), currency_symbol)
        total_retained += _to_decimal(entry.get('interest_retained', 0), currency_symbol)
        total_refund += _to_decimal(entry.get('interest_refund', 0), currency_symbol)
        total_accrued += _to_decimal(entry.get('interest_accrued', 0), currency_symbol)

    rounding = Decimal('0.01')

    if total_retained > 0:
        total_interest = (total_retained - total_refund).quantize(rounding, rounding=ROUND_HALF_UP)
    else:
        total_interest = total_interest_amt.quantize(rounding, rounding=ROUND_HALF_UP)

    total_savings = total_savings.quantize(rounding, rounding=ROUND_HALF_UP)
    interest_only_total = (total_interest + total_savings).quantize(rounding, rounding=ROUND_HALF_UP)

    summary: Dict[str, float] = {
        'totalInterest': float(total_interest),
        'total_interest': float(total_interest),
        'interestSavings': float(total_savings),
        'interestOnlyTotal': float(interest_only_total),
    }

    if total_retained:
        summary['retainedInterest'] = float(total_retained.quantize(rounding, rounding=ROUND_HALF_UP))
    if total_refund:
        summary['interestRefund'] = float(total_refund.quantize(rounding, rounding=ROUND_HALF_UP))
    if total_accrued:
        summary['total_interest_accrued'] = float(total_accrued.quantize(rounding, rounding=ROUND_HALF_UP))

    return summary


def generate_report_schedule(params: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, float]]:
    """Generate a detailed payment schedule for report output.


    Capital Payment Only already produces the desired report format. For
    Service + Capital the underlying engine yields a different schedule
    layout, so this helper re-runs the calculation using the Capital Payment
    Only breakdown to ensure all repayment options share an identical
    structure in generated reports while leaving standard calculations
    untouched.

    """
    calc = LoanCalculator()
    repayment_option = params.get('repayment_option')
    if repayment_option == 'service_and_capital':
        cap_params = params.copy()
        cap_params['repayment_option'] = 'capital_payment_only'
        calculation = calc.calculate_bridge_loan(cap_params)
    else:
        calculation = calc.calculate_bridge_loan(params)
    schedule = calculation.get('detailed_payment_schedule', [])

    summary: Dict[str, float] = {}

    # Remove any internal unrounded fields to keep report output stable
    for entry in schedule:
        for key in list(entry.keys()):
            if key.endswith('_raw'):
                del entry[key]

    # Recalculate interest fields using days_held to ensure consistency in reports
    if schedule:
        currency_symbol = schedule[0].get('opening_balance', '£')[0]
        gross_amount = Decimal(
            str(
                calculation.get(
                    'grossAmount',
                    calculation.get(
                        'gross_amount',
                        params.get('gross_amount', params.get('grossAmount', 0)),
                    ),
                )
            )
        )
        annual_rate = Decimal(
            str(
                params.get(
                    'annual_rate',
                    params.get(
                        'annualRate',
                        calculation.get('interestRate', calculation.get('annual_rate', 0)),
                    ),
                )
            )
        )
        days_per_year = Decimal('360') if params.get('use_360_days') else Decimal('365')
        daily_rate = annual_rate / Decimal('100') / days_per_year

        for row in schedule:
            start = row.get('start_period')
            end = row.get('end_period')
            if start and end:
                day_count = (datetime.strptime(end, '%d/%m/%Y') - datetime.strptime(start, '%d/%m/%Y')).days
                row['days_held'] = day_count
            else:
                day_count = int(row.get('days_held', 0))

            days = Decimal(str(day_count))
            capital_str = row.get('capital_outstanding', row.get('opening_balance', f"{currency_symbol}0"))
            capital_outstanding = Decimal(capital_str.replace(currency_symbol, '').replace(',', ''))

            retained_raw = gross_amount * daily_rate * days
            accrued_raw = capital_outstanding * daily_rate * days

            interest_retained = retained_raw.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            interest_accrued = accrued_raw.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            interest_refund = (interest_retained - interest_accrued).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            interest_saving = interest_refund

            row['interest_retained'] = f"{currency_symbol}{interest_retained:,.2f}"
            row['interest_accrued'] = f"{currency_symbol}{interest_accrued:,.2f}"
            row['interest_refund'] = f"{currency_symbol}{interest_refund:,.2f}"
            row['interest_saving'] = f"{currency_symbol}{interest_saving:,.2f}"

        summary = recalculate_summary(schedule)

    return schedule, summary
