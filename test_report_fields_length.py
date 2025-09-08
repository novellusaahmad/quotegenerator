import pytest

pytest.importorskip("flask")
pytest.importorskip("app")

from app import app, db
from models import LoanSummary, ReportFields


def _create_loan():
    with app.app_context():
        db.drop_all()
        db.create_all()
        loan = LoanSummary(loan_name="Test", loan_type="bridge")
        db.session.add(loan)
        db.session.commit()
        return loan.id


def test_broker_name_length_limit():
    loan_id = _create_loan()
    client = app.test_client()
    long_name = "a" * 201
    payload = {"broker_name": long_name, "brokerage": "ok"}

    res = client.post(f"/loan/{loan_id}/report-fields", json=payload)
    assert res.status_code == 400
    assert "error" in res.get_json()

    with app.app_context():
        rf = ReportFields.query.filter_by(loan_id=loan_id).first()
        assert rf is None
