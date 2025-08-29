"""Utility helpers for payment schedule generation used in reports."""

from typing import Any, Dict, List

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


def generate_report_schedule(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate a detailed payment schedule for report output.


    Capital Payment Only already produces the desired report format. For
    Service + Capital and Flexible Payment the underlying engine yields a
    different schedule layout, so this helper re-runs the calculation using
    the Capital Payment Only breakdown to ensure all three repayment options
    share an identical structure in generated reports while leaving standard
    calculations untouched.

    """
    calc = LoanCalculator()
    repayment_option = params.get('repayment_option')
    if repayment_option in ('service_and_capital', 'flexible_payment'):
        cap_params = params.copy()
        cap_params['repayment_option'] = 'capital_payment_only'
        if repayment_option == 'flexible_payment' and 'capital_repayment' not in cap_params:
            cap_params['capital_repayment'] = params.get('flexible_payment', params.get('flexiblePayment', 0))
        return calc.calculate_bridge_loan(cap_params).get('detailed_payment_schedule', [])
    return calc.calculate_bridge_loan(params).get('detailed_payment_schedule', [])
