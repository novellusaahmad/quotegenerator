import sys, types
import pytest
from decimal import Decimal
from calculations import LoanCalculator

# Provide minimal stub for dateutil.relativedelta to avoid external dependency
relativedelta_module = types.ModuleType('relativedelta')


class relativedelta:  # pragma: no cover - simple stub
    def __init__(self, months=0):
        self.months = months

    def __radd__(self, other):
        from datetime import date

        month = other.month - 1 + self.months
        year = other.year + month // 12
        month = month % 12 + 1
        day = min(
            other.day,
            [
                31,
                29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                31,
                30,
                31,
                30,
                31,
                31,
                30,
                31,
                30,
                31,
            ][month - 1],
        )
        return other.replace(year=year, month=month, day=day)


relativedelta_module.relativedelta = relativedelta
sys.modules['dateutil'] = types.ModuleType('dateutil')
sys.modules['dateutil'].relativedelta = relativedelta_module
sys.modules['dateutil.relativedelta'] = relativedelta_module

@pytest.mark.parametrize("repayment_option", ["service_only", "none"])
@pytest.mark.parametrize("amount_input", [
    {"gross_amount": 150000},
    {"amount_input_type": "net", "net_amount": 150000},
])
def test_simple_monthly_and_quarterly_interest(amount_input, repayment_option):
    calc = LoanCalculator()
    params = {
        "loan_type": "bridge",
        "repayment_option": repayment_option,
        "annual_rate": 12,
        "loan_term": 12,
        "payment_frequency": "monthly",
        "payment_timing": "arrears",
        "arrangement_fee_rate": 0,
        "legal_fees": 0,
        "site_visit_fee": 0,
        "title_insurance_rate": 0,
        "start_date": "2024-01-01",
    }
    params.update(amount_input)
    result = calc.calculate_bridge_loan(params)
    gross = Decimal(str(result["grossAmount"]))
    expected_monthly = gross * Decimal("0.12") / Decimal("12")
    expected_quarterly = gross * Decimal("0.12") / Decimal("4")
    assert result["monthlyInterestPayment"] == pytest.approx(float(expected_monthly), abs=0.01)
    assert result["quarterlyInterestPayment"] == pytest.approx(float(expected_quarterly), abs=0.01)
