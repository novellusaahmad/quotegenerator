import os
import pytest

# Use a separate SQLite database for testing
os.environ['DATABASE_URL'] = 'sqlite:///test_save_loan_empty_numeric.db'

# Skip module if Flask app dependencies are missing
pytest.importorskip("flask")
pytest.importorskip("app")
pytest.importorskip("models")

from app import app, db
from models import LoanSummary


def test_save_loan_handles_empty_numeric_fields():
    """Ensure /save-loan stores zero when numeric fields are empty strings"""
    with app.app_context():
        db.drop_all()
        db.create_all()

    client = app.test_client()

    payload = {
        "loanName": "EmptyNumericLoan",
        "loan_type": "development2",
        "currency": "GBP",
        "amount_input_type": "net",
        "net_amount": 100000,
        "property_value": 200000,
        "annual_rate": 5.0,
        "loan_term": 12,
        "repayment_option": "none",
        "arrangement_fee_percentage": 2.0,
        "legal_fees": 1500,
        "site_visit_fee": 500,
        "title_insurance_rate": 0.1,
        "payment_timing": "advance",
        "payment_frequency": "monthly",
        "capital_repayment": "",
        "flexible_payment": ""
    }

    response = client.post('/save-loan', json=payload)
    assert response.status_code == 200, response.get_data(as_text=True)

    with app.app_context():
        loan = LoanSummary.query.filter_by(loan_name="EmptyNumericLoan").first()
        assert loan is not None
        assert float(loan.capital_repayment or 0) == 0
        assert float(loan.flexible_payment or 0) == 0
