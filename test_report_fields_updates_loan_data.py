import pytest

pytest.importorskip("flask")
pytest.importorskip("app")

from app import app, db
from models import LoanSummary, LoanData


def _create_loan():
    with app.app_context():
        db.drop_all()
        db.create_all()
        loan = LoanSummary(loan_name="Test", loan_type="bridge")
        db.session.add(loan)
        db.session.commit()
        return loan.id


def test_report_fields_snapshot_updates_loan_data():
    loan_id = _create_loan()
    client = app.test_client()
    payload = {"client_name": "Client", "broker_name": "Broker", "brokerage": "Firm"}
    res = client.post(f"/loan/{loan_id}/report-fields", json=payload)
    assert res.status_code == 200
    assert res.get_json().get("success") is True

    with app.app_context():
        ld = LoanData.query.get(loan_id)
        assert ld is not None
        assert ld.client_name == "Client"
        assert ld.broker_name == "Broker"
        assert ld.brokerage == "Firm"
