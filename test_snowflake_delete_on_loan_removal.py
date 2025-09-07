import pytest

pytest.importorskip("flask")
pytest.importorskip("app")

import routes
from app import app, db
from models import LoanSummary


def test_delete_loan_triggers_snowflake(monkeypatch):
    client = app.test_client()

    # Create a simple loan record
    with app.app_context():
        loan = LoanSummary(loan_name="Test Loan", loan_type="bridge")
        db.session.add(loan)
        db.session.commit()
        loan_id = loan.id

    calls = []

    # Mock Snowflake utilities
    monkeypatch.setattr(routes, "test_snowflake_connection", lambda: calls.append("tested"))

    def fake_delete(table, column, value):
        calls.append((table, column, value))

    monkeypatch.setattr(routes, "delete_from_snowflake", fake_delete)

    res = client.delete(f"/api/loan/{loan_id}")
    assert res.status_code == 200
    body = res.get_json()
    assert body["success"] is True

    # Ensure Snowflake delete was invoked for both tables
    assert ("loan_summary", "id", loan_id) in calls
    assert ("payment_schedule", "loan_summary_id", loan_id) in calls
