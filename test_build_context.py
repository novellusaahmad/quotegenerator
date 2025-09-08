import pytest

from app import app  # Ensure application and models are initialised
from models import LoanSummary, ReportFields, LoanNote, User
from context_utils import build_context


def test_build_context_fields_and_token_replacement():
    user = User(first_name='Jane', last_name='Doe', email='jane@example.com')
    loan = LoanSummary(loan_name='Test Loan', loan_type='bridge', user=user)
    rf = ReportFields(
        client_name='Acme Corp',
        property_address='123 Example Street',
        debenture='Debenture',
        corporate_guarantor='Parent Co',
        broker_name='Broker Bob',
        brokerage='BB Brokerage',
        max_ltv=65.0,
        exit_fee_percent=1.5,
        commitment_fee=5000.0,
    )
    loan.report_fields = rf
    note = LoanNote(group='General', name='Client [CLIENT_NAME] at [PROPERTY_ADDRESS]')
    loan.loan_notes = [note]

    ctx = build_context(loan)

    assert ctx['client_name'] == 'Acme Corp'
    assert ctx['property_address'] == '123 Example Street'
    assert ctx['user_full_name'] == 'Jane Doe'
    assert 'loan_notes' not in ctx

    replacements = {f'[{k.upper()}]': v for k, v in ctx.items()}
    text = note.name
    for token, value in replacements.items():
        text = text.replace(token, str(value))

    assert text == 'Client Acme Corp at 123 Example Street'
