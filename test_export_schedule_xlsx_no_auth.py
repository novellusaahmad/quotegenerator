import pytest

pytest.importorskip("flask")
pytest.importorskip("app")

from app import app


def test_export_schedule_xlsx_no_auth():
    """Excel export endpoint should be accessible without authentication."""
    client = app.test_client()
    payload = {
        "payment_schedule": [],
        "tranche_schedule": [],
        "annual_rate": 10,
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
