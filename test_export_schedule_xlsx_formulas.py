import pytest
from io import BytesIO
from datetime import datetime
import openpyxl

from app import app


def test_export_schedule_xlsx_contains_formulas_and_dates():
    client = app.test_client()
    payload = {
        "payment_schedule": [
            {
                "date": "2024-01-01",
                "opening_balance": 1000,
                "payment_amount": 100,
                "interest_amount": 50,
                "closing_balance": 950,
            }
        ],
        "tranche_schedule": [
            {
                "tranche_number": 1,
                "release_date": "2024-01-01",
                "amount": 500,
                "interest_rate": 10,
            }
        ],
        "annual_rate": 10,
        "start_date": "2024-01-01",
        "loan_term": 12,
        "use_360_days": False,
    }
    res = client.post("/api/export-schedule-xlsx", json=payload)
    assert res.status_code == 200
    wb = openpyxl.load_workbook(BytesIO(res.data))

    # Ensure all expected sheets exist
    expected = {
        "Parameters",
        "Payment Schedule",
        "Payment Schedule Data",
        "Tranche Schedule",
        "Tranche Schedule Data",
    }
    assert expected.issubset(set(wb.sheetnames))

    pay_ws = wb["Payment Schedule"]
    assert isinstance(pay_ws["B2"].value, datetime)

    pay_form_ws = wb["Payment Schedule Data"]
    assert pay_form_ws["E2"].data_type == "f"
    assert pay_form_ws["E2"].value == "=C2*Parameters!$B$2"

    tranche_form_ws = wb["Tranche Schedule Data"]
    assert tranche_form_ws["D2"].data_type == "f"
    assert tranche_form_ws["D2"].value == "=Parameters!$B$6-B2"
