import os
import json

# Use a separate SQLite database for testing
os.environ['DATABASE_URL'] = 'sqlite:///test_save_loan.db'

from app import app, db
from models import LoanSummary


def test_save_loan_preserves_amount_input_type():
    """Ensure /save-loan stores provided amount_input_type"""
    with app.app_context():
        db.drop_all()
        db.create_all()

    client = app.test_client()

    payload = {
        "loanName": "Test Loan",
        "loan_type": "bridge",
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
        "payment_frequency": "monthly"
    }

    response = client.post('/save-loan', json=payload)
    assert response.status_code == 200, response.get_data(as_text=True)

    with app.app_context():
        loan = LoanSummary.query.filter_by(loan_name="Test Loan").first()
        assert loan is not None
        assert loan.amount_input_type == 'net'
