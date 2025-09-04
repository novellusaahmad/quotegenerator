import pytest

from app import app


def test_export_schedule_xlsx_handles_currency_strings():
    """Excel export should accept currency-formatted strings."""
    client = app.test_client()
    payload = {
        "payment_schedule": [
            {
                "date": "2024-01-01",
                "opening_balance": "£1,000,000.00",
                "payment_amount": "£10,000.00",
                "interest_amount": "£5,000.00",
                "closing_balance": "£990,000.00",
            }
        ],
        "tranche_schedule": [
            {
                "tranche_number": 1,
                "release_date": "2024-01-01",
                "amount": "£500,000.00",
                "interest_rate": "10",
            }
        ],
        "annual_rate": "10",
        "start_date": "2024-01-01",
        "loan_term": 12,
        "use_360_days": False,
    }
    res = client.post("/api/export-schedule-xlsx", json=payload)
    assert res.status_code == 200
    assert (
        res.headers.get("Content-Type")
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert res.data, "No file content returned"
