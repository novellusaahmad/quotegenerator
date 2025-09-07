"""
PDF Quote Generator for Novellus Loan Management System
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import tempfile
from datetime import datetime

def generate_quote_pdf(quote_data, application_data=None):
    """Generate PDF quote document"""
    # Create temporary file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        tmp_path = tmp_file.name
    
    # Create PDF document
    doc = SimpleDocTemplate(tmp_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph("Novellus Finance - Loan Quote", title_style))
    story.append(Spacer(1, 12))
    
    # Quote details table
    quote_details = [
        ['Quote ID:', str(quote_data.get('id', 'N/A'))],
        ['Date:', datetime.now().strftime('%d/%m/%Y')],
        ['Gross Amount:', f"£{quote_data.get('gross_amount', 0):,.2f}"],
        ['Net Advance:', f"£{quote_data.get('net_advance', 0):,.2f}"],
        ['Interest Rate:', f"{quote_data.get('interest_rate', 0):.2f}%"],
        ['Loan Term:', f"{quote_data.get('loan_term', 0)} months"],
        ['Monthly Payment:', f"£{quote_data.get('monthly_payment', 0):,.2f}"],
        ['Total Interest:', f"£{quote_data.get('total_interest', 0):,.2f}"],
    ]
    
    table = Table(quote_details, colWidths=[2*inch, 3*inch])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 24))
    
    # Footer
    footer_text = "This quote is subject to credit approval and full underwriting. Terms and conditions apply."
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER
    )
    story.append(Paragraph(footer_text, footer_style))
    
    # Build PDF
    doc.build(story)
    
    # Read the PDF content
    with open(tmp_path, 'rb') as f:
        pdf_content = f.read()
    
    # Clean up temporary file
    os.unlink(tmp_path)
    
    return pdf_content

def generate_professional_quote_docx(quote_data, application_data=None):
    """Generate professional DOCX quote document"""
    from docx import Document
    from docx.shared import Inches
    
    doc = Document()
    
    # Add title
    title = doc.add_heading('Novellus Finance - Loan Quote', 0)
    title.alignment = 1  # Center alignment
    
    # Add quote details
    doc.add_heading('Quote Details', level=1)
    
    table = doc.add_table(rows=8, cols=2)
    table.style = 'Table Grid'
    
    details = [
        ('Quote ID:', str(quote_data.get('id', 'N/A'))),
        ('Date:', datetime.now().strftime('%d/%m/%Y')),
        ('Gross Amount:', f"£{quote_data.get('gross_amount', 0):,.2f}"),
        ('Net Advance:', f"£{quote_data.get('net_advance', 0):,.2f}"),
        ('Interest Rate:', f"{quote_data.get('interest_rate', 0):.2f}%"),
        ('Loan Term:', f"{quote_data.get('loan_term', 0)} months"),
        ('Monthly Payment:', f"£{quote_data.get('monthly_payment', 0):,.2f}"),
        ('Total Interest:', f"£{quote_data.get('total_interest', 0):,.2f}"),
    ]
    
    for i, (key, value) in enumerate(details):
        table.cell(i, 0).text = key
        table.cell(i, 1).text = value
    
    # Add footer
    doc.add_paragraph()
    footer = doc.add_paragraph('This quote is subject to credit approval and full underwriting. Terms and conditions apply.')
    footer.alignment = 1  # Center alignment
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_file:
        doc.save(tmp_file.name)
        tmp_path = tmp_file.name
    
    # Read the content
    with open(tmp_path, 'rb') as f:
        docx_content = f.read()
    
    # Clean up
    os.unlink(tmp_path)
    
    return docx_content


def generate_loan_summary_docx(loan):
    """Generate DOCX loan summary report."""
    from docx import Document
    import tempfile

    doc = Document()

    doc.add_paragraph("Dear [•],")
    doc.add_paragraph(
        "Further to our correspondence, please see below our high-level terms subject to (i) valuation, (ii) planning appraisal, (iii) QS appraisal, (iv) due diligence and (v) legals:"
    )

    doc.add_heading("Loan Summary", level=1)

    table = doc.add_table(rows=8, cols=3)
    table.style = 'Table Grid'

    currency_symbol = '€' if getattr(loan, 'currency', 'GBP') == 'EUR' else '£'
    arr_fee_pct = f"{float(getattr(loan, 'arrangement_fee_percentage', 0) or 0):.2f}%"

    rows = [
        ("Valuation", currency_symbol, f"{float(getattr(loan, 'property_value', 0) or 0):,.2f}"),
        ("Gross Amount", currency_symbol, f"{float(getattr(loan, 'gross_amount', 0) or 0):,.2f}"),
        ("Term (Months)", "", str(getattr(loan, 'loan_term', 0) or 0)),
        (
            "Arrangement Fee",
            f"{arr_fee_pct} {currency_symbol}",
            f"{float(getattr(loan, 'arrangement_fee', 0) or 0):,.2f}",
        ),
        (
            "Legal Costs & Title Insurance*",
            currency_symbol,
            f"{float((getattr(loan, 'legal_costs', 0) or 0) + (getattr(loan, 'title_insurance', 0) or 0)):,.2f}",
        ),
        (
            "Number Months (Interest)",
            str(getattr(loan, 'loan_term', 0) or 0),
            f"{currency_symbol}{float(getattr(loan, 'total_interest', 0) or 0):,.2f}",
        ),
        (
            "Day 1 Net Advance",
            currency_symbol,
            f"{float((getattr(loan, 'day_1_advance', None) or getattr(loan, 'net_advance', 0) or 0)):,.2f}",
        ),
        (
            "Total Net Advance",
            currency_symbol,
            f"{float(getattr(loan, 'total_net_advance', 0) or 0):,.2f}",
        ),
    ]

    for i, (c1, c2, c3) in enumerate(rows):
        table.cell(i, 0).text = c1
        table.cell(i, 1).text = c2
        table.cell(i, 2).text = c3

    sections = [
        (
            "Security",
            [
                "First legal charge over the site located at [•] (the “Property”).",
                "[if applicable] First legal charge over the following assets (collectively, the \"Property\"):",
                "Debenture over [•] (the “Borrower”).",
                "A full personal guarantee from the directors and any shareholder or beneficial owner with equal to or greater than 20% ownership in the Borrower.",
                "[if applicable]A full corporate guarantee from [•] (optional: together with a charge over its shares) (the “Corporate Guarantor”).",
            ],
        ),
        (
            "Salient Points",
            [
                "*Legal Costs / Fees (including Title Insurance and site visit, if applicable) are estimated at this stage. The final net advance figures will need to be adjusted accordingly to reflect final costs including any other (as yet unquoted) deductions.",
                "[if applicable] [Broker fees to be paid directly by the Borrower or can be added to the Arrangement Fee (tbc).]",
                "The arrangement fee is €[•] i.e. 2.00% of the gross loan of which 50% is paid to the broker.[(of which 50% is paid to [Broker Name, Brokerage])],",
                f"The loan Term is {getattr(loan, 'loan_term', 0) or 0} months in total (the “Term”).",
                f"Day 1 Net Advance of {currency_symbol}{float((getattr(loan, 'day_1_advance', None) or getattr(loan, 'net_advance', 0) or 0)):,.2f} to fund the purchase of/form part of the development tranche of the Property.",
                "Breach of value condition, loan not to exceed [•]% LTV (gross) throughout the Term.",
                "There is a [•]% exit fee in the sum of €[•] that is payable upon the redemption of this loan. This is in addition to the fee referred to at clause [facility fee clause number] below.",
                "[If Term Loan] The following exit fees apply to the loan:",
                "(a) a 3.00% exit fee (in the sum of €[•]) that applies if the loan redeems at any time in year 1 of the Term (subject always to the minimum interest period);",
                "(b) 2.00% exit fee (in the sum of €[•]) that applies if the loan redeems at any time in year 2 of the Term; and",
                "(c) a 1.00% exit fee (in the sum of €[•]) that applies if the loan redeems at any time thereafter.",
                "For the avoidance of doubt, the exit fee is payable in addition to the fee referred to at clause [facility fee clause number] below.",
                "A commitment fee of €[•] is payable upon signing Novellus' non-binding offer letter. This fee shall only be refunded to the Borrower if the loan completes within 6 weeks from the date of Novellus’ NBOL.",
                "Facility Fee: 2.00% of the loan which will be payable by the Borrower if either (1) the loan is not repaid in full on or before the repayment date (as defined in the Facility Agreement ) or (2) an event of default pursuant to the Facility Agreement occurs (and has not been waived by Novellus). This is in addition to any exit fee.",
                "The minimum interest period is [•] months.",
                "[The retained] Interest is estimated, based on a drawing of €[•] per month during months [•]-[•] of the Term, [in addition to the Day 1 Net Advance].",
                "No Early Repayment Charges (ERCs) save for a minimum notice period of 28 days to repay (or interest equivalent).",
                "Interest to be serviced monthly in advance/arrears.",
                "The loan will be subject to interest and capital repayments throughout the Term. The minimum monthly payment shall be €[•] (to be applied as interest first with the balance applied to the loan as capital reduction(s)) and is payable monthly in arrears.",
                "Net advance includes the first month interest deduction of €[•].",
                "The interest rate is fixed at [•]% p.a. for the Term.",
                "An application fee of €495.00 is payable upon the acceptance of these terms.",
            ],
        ),
        ("Conditions", []),
        (
            "Standard AML Pre-Conditions",
            [
                "Satisfactory proof that the source of any introduced funds is legitimate (together with any supporting documentation required by Novellus to evidence this).",
                "Full satisfactory KYC for the Borrower [and Personal / Corporate Guarantor].",
                "Guarantor(s) Personal Public Service (PPS) number (evidenced by way of documentation duly certified by solicitor) and contact details as required by the Central Credit Register.",
                "[Documentary evidence of PPSN for the Personal Guarantor(s) certified as true copies by the Borrower’s / Personal Guarantor(s)’ solicitors.]",
                "Two proof of address documents for all individuals involved in the transaction (no older than 3 months prior to the date of drawdown) to be certified as true copies by the Borrower's solicitors. Valid photo ID(s) (for all individuals involved in the transaction) to be certified as true copies by the Borrower's solicitors.",
                "[if applicable] Certified structure chart of the Borrower [and Corporate Guarantor].",
            ],
        ),
        (
            "Standard Financial Pre-Conditions",
            [
                "Any existing director / shareholder loans and / or equity introduced into the Borrower (prior to and/or at any time during the Term) shall be fully subordinated to Novellus’ loan by way of intercreditor deed(s) signed between all relevant parties and Novellus.",
                "[Approval from a tax advisor appointed by Novellus (the costs of which shall be borne by the Borrower), to the satisfaction of Novellus, of the proposed structure of the transaction and refinancing of the director’s loan(s).]",
                "Last 3 months bank statements of the Borrower and [Personal / Corporate Guarantor] to be provided by their respective accountants.",
                "[If required by Novellus, Corporate Guarantor’s latest audited and filed accounts (including financial statements).]",
                "Borrower’s most recent management accounts for the last three years, up to [•] (to be certified by the Borrower’s accountant).",
                "Written confirmation from the Borrower’s and [Personal / Corporate Guarantor’s] accountants that all tax affairs of the Borrower and [Personal / Corporate Guarantor] are up to date and in order or up to date tax clearance certificates for the Borrower and [Personal / Corporate Guarantor].",
                "Borrower to evidence to Novellus’ satisfaction that it has the funds to cover the balance of funds required for completion of the development at the Property (including, but not limited to, all fees, taxes and ongoing costs).",
                "Asset & Liability statements from the Borrower(s) and [Corporate Guarantor] to be provided and certified by the Borrower’s accountants.",
                "Subject to the sale agreement being reviewed by Novellus, to its satisfaction, evidencing the purchase price of [•] and the Borrower evidencing it has the funds to cover the balance of funds required for the purchase together with all fees, taxes and ongoing costs.",
                "[if applicable][Details and background as to the arrangement concerning the director’s loan balance (including, but not limited to, a redemption statement(s))].",
                "[Novellus to be satisfied with current/projected trading performance of the Property (including, but not limited to, management accounts up to [•] (certified by the Borrower’s accountants).]",
            ],
        ),
        (
            "Standard General Conditions",
            [
                "Certificate(s) of Title (in PSL format) or Report(s) on Title in connection with the Property to be provided to the satisfaction of Novellus.",
                "Novellus to be satisfied with any commercial leases in place at the Property.",
                "The Borrower or Guarantor(s) shall not reside in the Property (or any part of it) and shall procure that none of the members of its family reside in the Property (or any part of it).",
                "The directors / officers and shareholders of the Borrower entity [and / or the Corporate Guarantor entity] shall not reside in the Property(ies) (or any part of it/them).",
                "[The Personal Guarantor shall not reside in the Property(ies) (or any part of it)/them and shall procure that none of the members of their family reside in the Property(ies) (or any part of it)/them].",
                "The Borrower [and the Corporate Guarantor] shall procure that none of the members of the families of any director / officer or shareholder of the Borrower entity [and / or the Corporate Guarantor entity] shall reside in the Property(ies) (or any part of it/them).",
                "Novellus will undertake an inspection of the Property periodically.",
                "The loan is subject to a full disclosure and details to be provided in relation to the background to the transaction and relationship(s) between relevant parties, to Novellus’ full satisfaction.",
                "Loan will be subject to (a) red-book valuation of the Property, addressed to Novellus, supporting the values presented [•] (including the “as is” value and the GDV), on a [90]-day, VP basis. The valuer is to be appointed by Novellus and paid for by the Borrower (TBD).",
                "Novellus Limited to be noted as first loss payee above €50,000 on the insurance policy covering the assets within this transaction.",
                "The Borrower’s firm of solicitors must have a minimum of 2 partners.",
            ],
        ),
        (
            "Development Conditions",
            [
                "Borrower to evidence to Novellus’ satisfaction that it has the resources available to cover the balance of funds required for completion of the development at the Property (including, but not limited to, all fees, taxes and ongoing costs).",
                "Cost of works (including contingencies) to be provided on each drawdown (after the Day 1 Net Advance) to a maximum amount of €[•] in total (to Novellus’ satisfaction).",
                "Loan will be subject to a structural engineer's review of the Property to Novellus’ satisfaction and a structural engineer’s report for the Property is to be provided / procured (on which Novellus will have reliance). If required, a structural engineer is to be appointed by Novellus and paid for by the Borrower (TBD).",
                "Loan will be subject to a planning review of the Property and a planning report for the Property is to be provided / procured (on which Novellus will have reliance). If required, a planning consultant is to be appointed by Novellus and paid for by the Borrower (TBD).",
                "Gross Development Value (GDV) of the Property to be appraised and approved by the Lender’s QS in advance of any funds being released.",
                "The Borrower shall provide a detailed schedule of proposed works with estimated costs (including contingencies), to be appraised and approved by Novellus' Quantity Surveyor (QS) in advance of any funds being released.",
                "[The Borrower’s QS and/or project manager will report monthly or at each drawdown request, with reports being provided to Novellus’ satisfaction. Novellus will appoint its own QS and conduct inspections of the Property every month (or as otherwise reasonably required), with all associated costs (including Novellus’ internal monitoring costs) to be paid and deducted in the manner set out above. The Borrower’s QS and/or project manager must also confirm total expenditure and compliance with planning requirements in conjunction with site visits.",
                "Subject to the development of the Property being completed by no later than month [•] of the Term (with all necessary certifications, sign offs and requisite approvals) and the Property put up for sale by no later than the end of month [•]of the Term with a reputable local agent, to Novellus’ satisfaction.",
            ],
        ),
        (
            "Financial Covenants",
            [
                "Maximum LTV [•]%",
                "Minimum Debt Service Cover Ratio – minimum of [•] based on [•].",
                "Covenant compliance certificate confirming the financial covenants for the Borrower to be provided within one month of each Interest Payment Date (as defined in the Facility Agreement) during the Term. Quarterly management profit & loss statements for the Borrower to be received with each covenant compliance certificate.",
                "Draft year-end financial statements for the Borrower to be provided annually, within 3 months of the company’s year-end, with full audited statements to be received not less than 120 days following the company’s financial year end.",
            ],
        ),
        (
            "Repayment Conditions",
            [
                "A reputable agent must be appointed by the Borrower within [•] weeks of drawdown of the loan to market the Property for sale, with the Property to be sold within the Term. The agent is to be appointed and paid for by the Borrower and approved by Novellus.",
                "Subject to the development of the Property being completed by no later than month [•] of the Term (with all necessary certifications, sign offs and requisite approvals) and the Property put up for sale by no later than the end of month [•] of the Term with a reputable local agent, to Novellus’ satisfaction.",
                "All net proceeds from the sale of the Property to be paid to Novellus in repayment of the loan. Borrower to provide regular sales updates in connection with the intended sale of the Property as part of an exit strategy for the loan.",
                "The Borrower shall, within [•] months of the drawdown date, enter into agreement(s) to lease the Property and provide evidence of the same (in the form of exchanged agreements) to Novellus’ satisfaction. Any such agreement(s) shall be subject to Novellus’ prior written approval.",
                "The Borrower will demonstrate to the satisfaction of Novellus, no later than 90 days prior to the end of the Term, its ability to repay the  loan at the end of the Term. In the event of a refinance, this will include:",
                "No later than 90 days prior to the end of the Term, the Borrower will provide Novellus with evidence of having secured refinance heads of terms, demonstrating sufficient funding available to discharge the Borrower’s liability to Novellus in full by the end of the Term; and",
                "No later than 45 days prior to the end of the Term, the Borrower will provide Novellus with evidence of having a signed facility letter reflecting the above-referenced refinance heads of terms, demonstrating sufficient funding available to discharge the Borrower’s liability to Novellus in full by the end of the Term.",
            ],
        ),
        (
            "Other Conditions",
            [
                "Subject to an evidenced clear path to exit.",
                "This quote will expire within 7 days of this email.",
                "[If the above is of interest to your client, please fill out the application form attached and arrange to pay the €495, bank details also attached. Should you have any questions, don't hesitate to contact us.]",
            ],
        ),
    ]

    for heading, bullets in sections:
        doc.add_heading(heading, level=1)
        for bullet in bullets:
            p = doc.add_paragraph(bullet)
            p.style = 'List Bullet'

    doc.add_paragraph("Yours sincerely, [or faithfully if Dear Sir],")
    doc.add_paragraph("[•]")
    doc.add_paragraph("For and on behalf of")
    doc.add_paragraph("Novellus Finance Limited")

    with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_file:
        doc.save(tmp_file.name)
        tmp_path = tmp_file.name

    with open(tmp_path, 'rb') as f:
        docx_content = f.read()

    os.unlink(tmp_path)
    return docx_content
