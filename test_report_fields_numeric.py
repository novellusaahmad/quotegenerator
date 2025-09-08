import pytest
from decimal import Decimal

# Skip module if Flask app dependencies are missing
pytest.importorskip("flask")
pytest.importorskip("app")

from app import app, db
from models import LoanSummary, ReportFields


def _create_loan():
    """Create a loan and return its ID with a fresh database."""
    with app.app_context():
        db.drop_all()
        db.create_all()
        loan = LoanSummary(loan_name="Test", loan_type="bridge")
        db.session.add(loan)
        db.session.commit()
        return loan.id


def test_report_fields_valid_numbers_saved():
    loan_id = _create_loan()
    client = app.test_client()
    payload = {
        "max_ltv": "70.5",
        "exit_fee_percent": "1.25",
        "commitment_fee": "5000",
    }

    res = client.post(f"/loan/{loan_id}/report-fields", json=payload)
    assert res.status_code == 200
    assert res.get_json()["success"] is True

    with app.app_context():
        rf = ReportFields.query.filter_by(loan_id=loan_id).first()
        assert rf.max_ltv == Decimal("70.5")
        assert rf.exit_fee_percent == Decimal("1.25")
        assert rf.commitment_fee == Decimal("5000")


def test_report_fields_invalid_number_returns_error():
    loan_id = _create_loan()
    client = app.test_client()
    payload = {
        "max_ltv": "not-a-number",
        "exit_fee_percent": "2",
        "commitment_fee": "1000",
    }

    res = client.post(f"/loan/{loan_id}/report-fields", json=payload)
    assert res.status_code == 400
    assert "error" in res.get_json()

    with app.app_context():
        rf = ReportFields.query.filter_by(loan_id=loan_id).first()
        assert rf is None


def test_report_fields_empty_strings_set_to_none():
    loan_id = _create_loan()
    client = app.test_client()
    payload = {
        "max_ltv": "",
        "exit_fee_percent": "",
        "commitment_fee": "",
    }

    res = client.post(f"/loan/{loan_id}/report-fields", json=payload)
    assert res.status_code == 200
    assert res.get_json()["success"] is True

    with app.app_context():
        rf = ReportFields.query.filter_by(loan_id=loan_id).first()
        assert rf.max_ltv is None
        assert rf.exit_fee_percent is None
        assert rf.commitment_fee is None

