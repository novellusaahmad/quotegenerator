from decimal import Decimal
import pytest
from calculations import LoanCalculator

@pytest.mark.parametrize(
    "repayment_option, extra",
    [
        ("service_and_capital", {"capital_repayment": 5000}),
        ("flexible_payment", {"flexible_payment": 5000}),
    ],
)
def test_interest_saving_in_schedule(repayment_option, extra):
    calc = LoanCalculator()
    params = {
        "loan_type": "bridge",
        "gross_amount": 100000,
        "annual_rate": 12,
        "loan_term": 12,
        "currency": "GBP",
        "repayment_option": repayment_option,
        "start_date": "2025-01-01",
    }
    params.update(extra)
    result = calc.calculate_bridge_loan(params)
    schedule = result.get("detailed_payment_schedule")
    assert schedule, "Schedule should not be empty"
    values = []
    for entry in schedule:
        assert "interest_saving" in entry
        val = Decimal(entry["interest_saving"].replace("£", "").replace(",", ""))
        assert val >= 0
        values.append(val)
    assert any(v > 0 for v in values)

    total_schedule_saving = sum(values)
    assert float(total_schedule_saving) == pytest.approx(
        result["interestSavings"], abs=0.01
    )
