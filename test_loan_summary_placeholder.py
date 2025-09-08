import io
from types import SimpleNamespace

from docx import Document

from pdf_quote_generator import generate_loan_summary_docx


def extract_text(doc_bytes):
    document = Document(io.BytesIO(doc_bytes))
    text = []
    for paragraph in document.paragraphs:
        text.append(paragraph.text)
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                text.append(cell.text)
    return "\n".join(text)


def test_placeholder_map_replaces_token():
    loan = SimpleNamespace(
        currency='GBP',
        arrangement_fee_percentage=0,
        arrangement_fee=0,
        property_value=0,
        gross_amount=0,
        loan_term=0,
        legal_costs=0,
        title_insurance=0,
        total_interest=0,
        day_1_advance=0,
        net_advance=0,
        total_net_advance=0,
        ltv_ratio=0,
        start_ltv=0,
    )
    extra_fields = {
        'max_ltv': 70,
        'note_templates': [
            {
                'text': 'Max LTV is [MAX_LTV]%',
                'placeholder_map': {'MAX_LTV': 'max_ltv'},
            }
        ],
    }

    doc_bytes = generate_loan_summary_docx(loan, extra_fields)
    text = extract_text(doc_bytes)

    assert 'Max LTV is 70%' in text
    assert '[MAX_LTV]' not in text


def test_placeholder_map_nested_path():
    loan = SimpleNamespace(
        currency='GBP',
        arrangement_fee_percentage=0,
        arrangement_fee=0,
        property_value=0,
        gross_amount=0,
        loan_term=0,
        legal_costs=0,
        title_insurance=0,
        total_interest=0,
        day_1_advance=0,
        net_advance=0,
        total_net_advance=0,
        ltv_ratio=0,
        start_ltv=0,
    )

    extra_fields = {
        'report_fields': {'max_ltv': 60},
        'note_templates': [
            {
                'text': 'Max LTV is [MAX_LTV]%',
                'placeholder_map': {'MAX_LTV': 'report_fields.max_ltv'},
            }
        ],
    }

    doc_bytes = generate_loan_summary_docx(loan, extra_fields)
    text = extract_text(doc_bytes)

    assert 'Max LTV is 60%' in text
    assert '[MAX_LTV]' not in text
