import routes


def test_placeholder_options_includes_loan_summary_id():
    placeholder_options = [f"loan_data.{col.name}" for col in routes.LoanData.__table__.columns]
    assert "loan_data.loan_summary_id" in placeholder_options


def test_placeholder_options_include_new_summary_fields():
    placeholder_options = [f"loan_data.{col.name}" for col in routes.LoanData.__table__.columns]
    expected = {
        "loan_data.currency_symbol",
        "loan_data.gross_amount_percentage",
        "loan_data.ltv_target",
        "loan_data.monthly_interest_payment",
        "loan_data.quarterly_interest_payment",
    }
    assert expected.issubset(set(placeholder_options))
