import io
import os
from docx import Document

os.environ["DATABASE_URL"] = "sqlite:///test.db"

from app import app, db
from models import LoanSummary, ReportFields, LoanNote


def _setup_loan_and_note():
    """Reset DB and create a loan with a note using MAX_LTV placeholder."""
    with app.app_context():
        db.drop_all()
        db.create_all()
        loan = LoanSummary(loan_name="TestLoan", loan_type="bridge")
        db.session.add(loan)
        note = LoanNote(
            group="General",
            name="Max LTV is [MAX_LTV]%",
            placeholder_map={"MAX_LTV": "report_fields.max_ltv"},
            add_flag=True,
        )
        db.session.add(note)
        db.session.commit()
        return loan.id


def _extract_text(doc_bytes):
    doc = Document(io.BytesIO(doc_bytes))
    text = []
    for p in doc.paragraphs:
        text.append(p.text)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                text.append(cell.text)
    return "\n".join(text)


def test_download_summary_docx_post_uses_report_fields():
    loan_id = _setup_loan_and_note()
    client = app.test_client()
    payload = {"max_ltv": 70}
    res = client.post(f"/loan/{loan_id}/summary-docx", json=payload)
    assert res.status_code == 200
    text = _extract_text(res.data)
    assert "Max LTV is 70%" in text
    assert "[MAX_LTV]" not in text


def test_download_summary_docx_get_uses_saved_report_fields():
    loan_id = _setup_loan_and_note()
    with app.app_context():
        rf = ReportFields(loan_id=loan_id, max_ltv=55)
        db.session.add(rf)
        db.session.commit()
        assert LoanNote.query.count() == 1
    client = app.test_client()
    res = client.get(f"/loan/{loan_id}/summary-docx")
    assert res.status_code == 200
    text = _extract_text(res.data)
    assert "Max LTV is 55.0%" in text
    assert "[MAX_LTV]" not in text
