import routes


def test_placeholder_options_includes_loan_summary_id():
    placeholder_options = [f"loan_data.{col.name}" for col in routes.LoanData.__table__.columns]
    assert "loan_data.loan_summary_id" in placeholder_options
