from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='borrower')  # borrower, lender
    phone = db.Column(db.String(20))
    company = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    applications = db.relationship('Application', foreign_keys='Application.user_id', backref='user', lazy=True)
    documents = db.relationship('Document', foreign_keys='Document.user_id', backref='user', lazy=True)
    loan_summaries = db.relationship('LoanSummary', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Basic Information
    loan_type = db.Column(db.String(20), nullable=False)  # bridge, term, development
    loan_purpose = db.Column(db.Text)
    
    # Property Information
    property_address = db.Column(db.Text, nullable=False)
    property_type = db.Column(db.String(50))
    property_value = db.Column(db.Numeric(15, 2), nullable=False)
    purchase_price = db.Column(db.Numeric(15, 2))
    
    # Loan Details
    loan_amount = db.Column(db.Numeric(15, 2), nullable=False)
    loan_term = db.Column(db.Integer, nullable=False)  # months
    interest_rate = db.Column(db.Numeric(5, 3))
    ltv_ratio = db.Column(db.Numeric(5, 2))
    
    # Development Details (for development loans)
    development_type = db.Column(db.String(50))
    number_of_units = db.Column(db.Integer)
    estimated_gdv = db.Column(db.Numeric(15, 2))
    development_timeline = db.Column(db.Integer)  # months
    
    # Financial Information
    monthly_income = db.Column(db.Numeric(12, 2))
    annual_income = db.Column(db.Numeric(12, 2))
    existing_debt = db.Column(db.Numeric(12, 2))
    credit_score = db.Column(db.Integer)
    
    # Application Status
    status = db.Column(db.String(20), default='draft')  # draft, submitted, under_review, approved, rejected
    submitted_at = db.Column(db.DateTime)
    reviewed_at = db.Column(db.DateTime)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    quotes = db.relationship('Quote', backref='application', lazy=True)
    documents = db.relationship('Document', backref='application', lazy=True)
    payments = db.relationship('Payment', backref='application', lazy=True)
    communications = db.relationship('Communication', backref='application', lazy=True)
    reviewer = db.relationship('User', foreign_keys=[reviewer_id])

class Quote(db.Model):
    __tablename__ = 'quotes'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Quote Details
    gross_amount = db.Column(db.Numeric(15, 2), nullable=False)
    net_amount = db.Column(db.Numeric(15, 2), nullable=False)
    interest_rate = db.Column(db.Numeric(5, 3), nullable=False)
    loan_term = db.Column(db.Integer, nullable=False)
    
    # Fees
    arrangement_fee = db.Column(db.Numeric(10, 2), default=0)
    legal_fees = db.Column(db.Numeric(10, 2), default=0)
    valuation_fee = db.Column(db.Numeric(10, 2), default=0)
    title_insurance = db.Column(db.Numeric(10, 2), default=0)
    exit_fee = db.Column(db.Numeric(10, 2), default=0)
    
    # Calculated Values
    monthly_payment = db.Column(db.Numeric(10, 2))
    total_interest = db.Column(db.Numeric(15, 2))
    total_amount = db.Column(db.Numeric(15, 2))
    ltv_ratio = db.Column(db.Numeric(5, 2))
    
    # Quote Status
    status = db.Column(db.String(20), default='draft')  # draft, sent, accepted, rejected
    valid_until = db.Column(db.DateTime)
    
    # Payment Schedule (JSON)
    payment_schedule = db.Column(db.Text)  # JSON string
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by])

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Document Details
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    mime_type = db.Column(db.String(100))
    
    # Document Type
    document_type = db.Column(db.String(50), nullable=False)  # valuation, financial_statement, id_document, etc.
    description = db.Column(db.Text)
    
    # Status
    status = db.Column(db.String(20), default='uploaded')  # uploaded, reviewed, approved, rejected
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    
    # Payment Details
    payment_type = db.Column(db.String(30), nullable=False)  # arrangement_fee, monthly_payment, principal, etc.
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    currency = db.Column(db.String(3), default='GBP')
    
    # Payment Status
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed, cancelled
    due_date = db.Column(db.DateTime)
    paid_date = db.Column(db.DateTime)
    
    # Payment Method
    payment_method = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100))
    
    # Description
    description = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Communication(db.Model):
    __tablename__ = 'communications'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    from_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Message Details
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='message')  # message, status_update, notification
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    from_user = db.relationship('User', foreign_keys=[from_user_id])
    to_user = db.relationship('User', foreign_keys=[to_user_id])


class LoanSummary(db.Model):
    __tablename__ = 'loan_summary'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Allow null for demo purposes
    
    # Loan identification
    loan_name = db.Column(db.String(200), nullable=False)
    version = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Loan basic details
    loan_type = db.Column(db.String(50), nullable=False)  # bridge, term, development
    currency = db.Column(db.String(10), default='GBP')
    
    # Input parameters
    amount_input_type = db.Column(db.String(20))  # gross, net
    gross_amount = db.Column(db.Numeric(15, 2))
    net_amount = db.Column(db.Numeric(15, 2))
    property_value = db.Column(db.Numeric(15, 2))
    
    # Interest and term details
    interest_rate = db.Column(db.Numeric(8, 4))
    loan_term = db.Column(db.Integer)  # in months
    loan_term_days = db.Column(db.Integer)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    
    # Repayment details
    repayment_option = db.Column(db.String(50))
    payment_timing = db.Column(db.String(20))  # in_advance, in_arrears
    payment_frequency = db.Column(db.String(20))  # monthly, quarterly
    capital_repayment = db.Column(db.Numeric(15, 2))
    flexible_payment = db.Column(db.Numeric(15, 2))
    
    # Fees
    arrangement_fee = db.Column(db.Numeric(15, 2))
    arrangement_fee_percentage = db.Column(db.Numeric(8, 4))
    legal_costs = db.Column(db.Numeric(15, 2))
    site_visit_fee = db.Column(db.Numeric(15, 2))
    title_insurance = db.Column(db.Numeric(15, 2))
    
    # Calculation results
    total_interest = db.Column(db.Numeric(15, 2))
    net_advance = db.Column(db.Numeric(15, 2))
    total_net_advance = db.Column(db.Numeric(15, 2))
    monthly_payment = db.Column(db.Numeric(15, 2))
    quarterly_payment = db.Column(db.Numeric(15, 2))
    
    # LTV calculations
    start_ltv = db.Column(db.Numeric(8, 4))
    end_ltv = db.Column(db.Numeric(8, 4))
    
    # Interest savings (for flexible payments)
    interest_only_total = db.Column(db.Numeric(15, 2))
    interest_savings = db.Column(db.Numeric(15, 2))
    savings_percentage = db.Column(db.Numeric(8, 4))
    
    # Development loan specific
    day_1_advance = db.Column(db.Numeric(15, 2))
    user_input_day_1_advance = db.Column(db.Numeric(15, 2))
    tranches_data = db.Column(db.Text)  # JSON string for tranche details
    
    # Relationship to payment schedule
    payment_schedule = db.relationship('PaymentSchedule', backref='loan', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<LoanSummary {self.loan_name} v{self.version}>'


class PaymentSchedule(db.Model):
    __tablename__ = 'payment_schedule'
    
    id = db.Column(db.Integer, primary_key=True)
    loan_summary_id = db.Column(db.Integer, db.ForeignKey('loan_summary.id'), nullable=False)
    
    # Payment schedule details
    period_number = db.Column(db.Integer, nullable=False)
    payment_date = db.Column(db.Date)
    
    # Balance details
    opening_balance = db.Column(db.Numeric(15, 2))
    closing_balance = db.Column(db.Numeric(15, 2))
    balance_change = db.Column(db.String(50))
    
    # Payment breakdown
    total_payment = db.Column(db.Numeric(15, 2))
    interest_amount = db.Column(db.Numeric(15, 2))
    principal_payment = db.Column(db.Numeric(15, 2))
    tranche_release = db.Column(db.Numeric(15, 2))
    
    # Calculation details
    interest_calculation = db.Column(db.String(500))
    
    def __repr__(self):
        return f'<PaymentSchedule Period {self.period_number} for Loan {self.loan_summary_id}>'
