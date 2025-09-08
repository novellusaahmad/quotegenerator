#!/usr/bin/env python3
"""
Database initialization script for Novellus Loan Management System
This script creates all database tables and performs initial setup
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def init_database():
    """Initialize the database with all required tables"""
    try:
        # Add current directory to Python path
        current_dir = Path(__file__).parent.absolute()
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))
        
        # Import Flask app and database
        from app import app, db
        
        # Create application context
        with app.app_context():
            logger.info("Creating database tables...")
            
            # Import all models to ensure they're registered
            try:
                import models
                logger.info("Models imported successfully")
                
                # Verify critical loan calculator models are available
                from models import (
                    LoanSummary,
                    PaymentSchedule,
                    User,
                    Application,
                    LoanNote,
                )
                logger.info(
                    "Loan calculator storage models verified: LoanSummary, PaymentSchedule"
                )
                
            except ImportError as e:
                logger.warning(f"Could not import models: {e}")
                logger.info("Proceeding with basic table creation...")
            
            # Create all tables
            db.create_all()
            logger.info("Database tables created")

            # Seed LoanNote data if empty
            if 'loan_notes' in db.inspect(db.engine).get_table_names():
                if LoanNote.query.count() == 0:
                    logger.info("Seeding Loan Notes table")
                    loan_notes_data = [
                        {"group": "Salient Points", "name": "Legal Costs / Fees (including Title Insurance and site visit, if applicable) are estimated at this stage. The final net advance figures will need to be adjusted accordingly to reflect final costs including any other (as yet unquoted) deductions.", "add_flag": True},
                        {"group": "Salient Points", "name": "[if applicable] [Broker fees to be paid directly by the Borrower or can be added to the Arrangement Fee (tbc).]", "add_flag": True},
                        {"group": "Salient Points", "name": "The arrangement fee is €4,000.00 i.e. 2.00% of the gross loan of which 50% is paid to the broker (of which 50% is paid to Broker, Broker1).", "add_flag": True},
                        {"group": "Salient Points", "name": "The loan Term is 13 months in total (the \u201cTerm\u201d).", "add_flag": True},
                        {"group": "Salient Points", "name": "Day 1 Net Advance of €166,691.40 to fund the purchase of/form part of the development tranche of the Property.", "add_flag": True},
                        {"group": "Salient Points", "name": "Breach of value condition, loan not to exceed 70.00% LTV (gross) throughout the Term.", "add_flag": True},
                        {"group": "Salient Points", "name": "There is a 2.00% exit fee in the sum of €4,000.00 that is payable upon the redemption of this loan. This is in addition to the fee referred to at clause [facility fee clause number] below.", "add_flag": True},
                        {"group": "Salient Points", "name": "[If Term Loan] The following exit fees apply to the loan: (a) a 3.00% exit fee (in the sum of €[\u2022]) that applies if the loan redeems at any time in year 1 of the Term (subject always to the minimum interest period); (b) 2.00% exit fee (in the sum of €[\u2022]) that applies if the loan redeems at any time in year 2 of the Term; and (c) a 1.00% exit fee (in the sum of €[\u2022]) that applies if the loan redeems at any time thereafter.", "add_flag": True},
                        {"group": "Salient Points", "name": "For the avoidance of doubt, the exit fee is payable in addition to the fee referred to at clause [facility fee clause number] below.", "add_flag": True},
                        {"group": "Salient Points", "name": "A commitment fee of €40,000.00 is payable upon signing Novellus' non-binding offer letter. This fee shall only be refunded to the Borrower if the loan completes within 6 weeks from the date of Novellus\u2019 NBOL.", "add_flag": True},
                        {"group": "Salient Points", "name": "Facility Fee: 2.00% of the loan which will be payable by the Borrower if either (1) the loan is not repaid in full on or before the repayment date (as defined in the Facility Agreement ) or (2) an event of default pursuant to the Facility Agreement occurs (and has not been waived by Novellus). This is in addition to any exit fee.", "add_flag": True},
                        {"group": "Salient Points", "name": "The minimum interest period is [\u2022] months.", "add_flag": True},
                        {"group": "Salient Points", "name": "[The retained] Interest is estimated, based on a drawing of €[\u2022] per month during months [\u2022]-[\u2022] of the Term, [in addition to the Day 1 Net Advance].", "add_flag": True},
                        {"group": "Salient Points", "name": "No Early Repayment Charges (ERCs) save for a minimum notice period of 28 days to repay (or interest equivalent).", "add_flag": True},
                        {"group": "Salient Points", "name": "Interest to be serviced monthly in advance/arrears.", "add_flag": True},
                        {"group": "Salient Points", "name": "The loan will be subject to interest and capital repayments throughout the Term. The minimum monthly payment shall be €[\u2022] (to be applied as interest first with the balance applied to the loan as capital reduction(s)) and is payable monthly in arrears.", "add_flag": True},
                        {"group": "Salient Points", "name": "Net advance includes the first month interest deduction of €0.00.", "add_flag": True},
                        {"group": "Salient Points", "name": "The interest rate is fixed at 12.00% p.a. for the Term.", "add_flag": True},
                        {"group": "Salient Points", "name": "An application fee of €495.00 is payable upon the acceptance of these terms.", "add_flag": True},

                        {"group": "Standard AML Pre-Conditions", "name": "Satisfactory proof that the source of any introduced funds is legitimate (together with any supporting documentation required by Novellus to evidence this).", "add_flag": True},
                        {"group": "Standard AML Pre-Conditions", "name": "Full satisfactory KYC for the Borrower [and Personal / Corporate Guarantor].", "add_flag": True},
                        {"group": "Standard AML Pre-Conditions", "name": "Guarantor(s) Personal Public Service (PPS) number (evidenced by way of documentation duly certified by solicitor) and contact details as required by the Central Credit Register.", "add_flag": True},
                        {"group": "Standard AML Pre-Conditions", "name": "[Documentary evidence of PPSN for the Personal Guarantor(s) certified as true copies by the Borrower\u2019s / Personal Guarantor(s)\u2019 solicitors.]", "add_flag": True},
                        {"group": "Standard AML Pre-Conditions", "name": "Two proof of address documents for all individuals involved in the transaction (no older than 3 months prior to the date of drawdown) to be certified as true copies by the Borrower's solicitors. Valid photo ID(s) (for all individuals involved in the transaction) to be certified as true copies by the Borrower's solicitors.", "add_flag": True},
                        {"group": "Standard AML Pre-Conditions", "name": "[if applicable] Certified structure chart of the Borrower [and Corporate Guarantor].", "add_flag": True},

                        {"group": "Standard Financial Pre-Conditions", "name": "Any existing director / shareholder loans and / or equity introduced into the Borrower (prior to and/or at any time during the Term) shall be fully subordinated to Novellus\u2019 loan by way of intercreditor deed(s) signed between all relevant parties and Novellus.", "add_flag": True},
                        {"group": "Standard Financial Pre-Conditions", "name": "[Approval from a tax advisor appointed by Novellus (the costs of which shall be borne by the Borrower), to the satisfaction of Novellus, of the proposed structure of the transaction and refinancing of the director\u2019s loan(s).]", "add_flag": True},
                        {"group": "Standard Financial Pre-Conditions", "name": "Last 3 months bank statements of the Borrower and [Personal / Corporate Guarantor] to be provided by their respective accountants.", "add_flag": True},
                        {"group": "Standard Financial Pre-Conditions", "name": "[If required by Novellus, Corporate Guarantor\u2019s latest audited and filed accounts (including financial statements).]", "add_flag": True},
                        {"group": "Standard Financial Pre-Conditions", "name": "Borrower\u2019s most recent management accounts for the last three years, up to [\u2022] (to be certified by the Borrower\u2019s accountant).", "add_flag": True},
                        {"group": "Standard Financial Pre-Conditions", "name": "Written confirmation from the Borrower\u2019s and [Personal / Corporate Guarantor\u2019s] accountants that all tax affairs of the Borrower and [Personal / Corporate Guarantor] are up to date and in order or up to date tax clearance certificates for the Borrower and [Personal / Corporate Guarantor].", "add_flag": True},
                        {"group": "Standard Financial Pre-Conditions", "name": "Borrower to evidence to Novellus\u2019 satisfaction that it has the funds to cover the balance of funds required for completion of the development at the Property (including, but not limited to, all fees, taxes and ongoing costs).", "add_flag": True},
                        {"group": "Standard Financial Pre-Conditions", "name": "Asset & Liability statements from the Borrower(s) and [Corporate Guarantor] to be provided and certified by the Borrower\u2019s accountants.", "add_flag": True},
                        {"group": "Standard Financial Pre-Conditions", "name": "Subject to the sale agreement being reviewed by Novellus, to its satisfaction, evidencing the purchase price of [\u2022] and the Borrower evidencing it has the funds to cover the balance of funds required for the purchase together with all fees, taxes and ongoing costs.", "add_flag": True},
                        {"group": "Standard Financial Pre-Conditions", "name": "[if applicable][Details and background as to the arrangement concerning the director\u2019s loan balance (including, but not limited to, a redemption statement(s))].", "add_flag": True},
                        {"group": "Standard Financial Pre-Conditions", "name": "[Novellus to be satisfied with current/projected trading performance of the Property (including, but not limited to, management accounts up to [\u2022] (certified by the Borrower\u2019s accountants).]", "add_flag": True},

                        {"group": "Standard General Conditions", "name": "Certificate(s) of Title (in PSL format) or Report(s) on Title in connection with the Property to be provided to the satisfaction of Novellus.", "add_flag": True},
                        {"group": "Standard General Conditions", "name": "Novellus to be satisfied with any commercial leases in place at the Property.", "add_flag": True},
                        {"group": "Standard General Conditions", "name": "The Borrower or Guarantor(s) shall not reside in the Property (or any part of it) and shall procure that none of the members of its family reside in the Property (or any part of it).", "add_flag": True},
                        {"group": "Standard General Conditions", "name": "The directors / officers and shareholders of the Borrower entity [and / or the Corporate Guarantor entity] shall not reside in the Property(ies) (or any part of it/them).", "add_flag": True},
                        {"group": "Standard General Conditions", "name": "[The Personal Guarantor shall not reside in the Property(ies) (or any part of it)/them and shall procure that none of the members of their family reside in the Property(ies) (or any part of it)/them].", "add_flag": True},
                        {"group": "Standard General Conditions", "name": "The Borrower [and the Corporate Guarantor] shall procure that none of the members of the families of any director / officer or shareholder of the Borrower entity [and / or the Corporate Guarantor entity] shall reside in the Property(ies) (or any part of it/them).", "add_flag": True},
                        {"group": "Standard General Conditions", "name": "Novellus will undertake an inspection of the Property periodically.", "add_flag": True},
                        {"group": "Standard General Conditions", "name": "The loan is subject to a full disclosure and details to be provided in relation to the background to the transaction and relationship(s) between relevant parties, to Novellus\u2019 full satisfaction.", "add_flag": True},
                        {"group": "Standard General Conditions", "name": "Loan will be subject to (a) red-book valuation of the Property, addressed to Novellus, supporting the values presented [\u2022] (including the \u201cas is\u201d value and the GDV), on a [90]-day, VP basis. The valuer is to be appointed by Novellus and paid for by the Borrower (TBD).", "add_flag": True},
                        {"group": "Standard General Conditions", "name": "Novellus Limited to be noted as first loss payee above €50,000 on the insurance policy covering the assets within this transaction.", "add_flag": True},
                        {"group": "Standard General Conditions", "name": "The Borrower\u2019s firm of solicitors must have a minimum of 2 partners.", "add_flag": True},

                        {"group": "Development Conditions", "name": "Borrower to evidence to Novellus\u2019 satisfaction that it has the resources available to cover the balance of funds required for completion of the development at the Property (including, but not limited to, all fees, taxes and ongoing costs).", "add_flag": True},
                        {"group": "Development Conditions", "name": "Cost of works (including contingencies) to be provided on each drawdown (after the Day 1 Net Advance) to a maximum amount of €[\u2022] in total (to Novellus\u2019 satisfaction).", "add_flag": True},
                        {"group": "Development Conditions", "name": "Loan will be subject to a structural engineer's review of the Property to Novellus\u2019 satisfaction and a structural engineer\u2019s report for the Property is to be provided / procured (on which Novellus will have reliance). If required, a structural engineer is to be appointed by Novellus and paid for by the Borrower (TBD).", "add_flag": True},
                        {"group": "Development Conditions", "name": "Loan will be subject to a planning review of the Property and a planning report for the Property is to be provided / procured (on which Novellus will have reliance). If required, a planning consultant is to be appointed by Novellus and paid for by the Borrower (TBD).", "add_flag": True},
                        {"group": "Development Conditions", "name": "Gross Development Value (GDV) of the Property to be appraised and approved by the Lender\u2019s QS in advance of any funds being released.", "add_flag": True},
                        {"group": "Development Conditions", "name": "The Borrower shall provide a detailed schedule of proposed works with estimated costs (including contingencies), to be appraised and approved by Novellus' Quantity Surveyor (QS) in advance of any funds being released.", "add_flag": True},
                        {"group": "Development Conditions", "name": "[The Borrower\u2019s QS and/or project manager will report monthly or at each drawdown request, with reports being provided to Novellus\u2019 satisfaction. Novellus will appoint its own QS and conduct inspections of the Property every month (or as otherwise reasonably required), with all associated costs (including Novellus\u2019 internal monitoring costs) to be paid and deducted in the manner set out above. The Borrower\u2019s QS and/or project manager must also confirm total expenditure and compliance with planning requirements in conjunction with site visits.", "add_flag": True},
                        {"group": "Development Conditions", "name": "Subject to the development of the Property being completed by no later than month [\u2022] of the Term (with all necessary certifications, sign offs and requisite approvals) and the Property put up for sale by no later than the end of month [\u2022]of the Term with a reputable local agent, to Novellus\u2019 satisfaction.", "add_flag": True},

                        {"group": "Financial Covenants", "name": "Maximum LTV 70.00%", "add_flag": True},
                        {"group": "Financial Covenants", "name": "Minimum Debt Service Cover Ratio \u2013 minimum of [\u2022] based on [\u2022].", "add_flag": True},
                        {"group": "Financial Covenants", "name": "Covenant compliance certificate confirming the financial covenants for the Borrower to be provided within one month of each Interest Payment Date (as defined in the Facility Agreement) during the Term. Quarterly management profit & loss statements for the Borrower to be received with each covenant compliance certificate.", "add_flag": True},
                        {"group": "Financial Covenants", "name": "Draft year-end financial statements for the Borrower to be provided annually, within 3 months of the company\u2019s year-end, with full audited statements to be received not less than 120 days following the company\u2019s financial year end.", "add_flag": True},

                        {"group": "Repayment Conditions", "name": "A reputable agent must be appointed by the Borrower within [\u2022] weeks of drawdown of the loan to market the Property for sale, with the Property to be sold within the Term. The agent is to be appointed and paid for by the Borrower and approved by Novellus.", "add_flag": True},
                        {"group": "Repayment Conditions", "name": "Subject to the development of the Property being completed by no later than month [\u2022] of the Term (with all necessary certifications, sign offs and requisite approvals) and the Property put up for sale by no later than the end of month [\u2022] of the Term with a reputable local agent, to Novellus\u2019 satisfaction.", "add_flag": True},
                        {"group": "Repayment Conditions", "name": "All net proceeds from the sale of the Property to be paid to Novellus in repayment of the loan. Borrower to provide regular sales updates in connection with the intended sale of the Property as part of an exit strategy for the loan.", "add_flag": True},
                        {"group": "Repayment Conditions", "name": "The Borrower shall, within [\u2022] months of the drawdown date, enter into agreement(s) to lease the Property and provide evidence of the same (in the form of exchanged agreements) to Novellus\u2019 satisfaction. Any such agreement(s) shall be subject to Novellus\u2019 prior written approval.", "add_flag": True},
                        {"group": "Repayment Conditions", "name": "The Borrower will demonstrate to the satisfaction of Novellus, no later than 90 days prior to the end of the Term, its ability to repay the  loan at the end of the Term. In the event of a refinance, this will include: No later than 90 days prior to the end of the Term, the Borrower will provide Novellus with evidence of having secured refinance heads of terms, demonstrating sufficient funding available to discharge the Borrower\u2019s liability to Novellus in full by the end of the Term; and No later than 45 days prior to the end of the Term, the Borrower will provide Novellus with evidence of having a signed facility letter reflecting the above-referenced refinance heads of terms, demonstrating sufficient funding available to discharge the Borrower\u2019s liability to Novellus in full by the end of the Term.", "add_flag": True},

                        {"group": "Other Conditions", "name": "Subject to an evidenced clear path to exit.", "add_flag": True},
                        {"group": "Other Conditions", "name": "This quote will expire within 7 days of this email.", "add_flag": True},
                        {"group": "Other Conditions", "name": "[If the above is of interest to your client, please fill out the application form attached and arrange to pay the €495, bank details also attached. Should you have any questions, don't hesitate to contact us.]", "add_flag": True},
                    ]
                    for note in loan_notes_data:
                        db.session.add(LoanNote(**note))
                    db.session.commit()
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if tables:
                logger.info(f"Database initialized successfully with tables: {', '.join(sorted(tables))}")
                
                # Specifically verify loan calculator tables
                required_tables = ['loan_summary', 'payment_schedule', 'users']
                missing_tables = [table for table in required_tables if table not in tables]
                
                if missing_tables:
                    logger.warning(f"Missing critical tables: {', '.join(missing_tables)}")
                    return False
                else:
                    logger.info("✓ All loan calculator storage tables created successfully")
                    
            else:
                logger.warning("No tables found after creation - this may indicate a problem")
            
            # Check database connection type
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            if 'postgresql' in db_uri:
                logger.info("✓ PostgreSQL database connection confirmed")
            else:
                logger.warning(f"⚠️  Unexpected database type in URI: {db_uri}")
            
            logger.info("Database initialization completed successfully!")
            return True
            
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_database_connection():
    """Test database connection and loan calculator storage operations"""
    try:
        from app import app, db
        
        with app.app_context():
            # Test basic database operations
            logger.info("Testing database connection...")
            
            # Execute a simple query
            with db.engine.connect() as connection:
                result = connection.execute(db.text("SELECT 1")).fetchone()
            if result:
                logger.info("✓ Database connection test successful!")
                
                # Test loan calculator storage tables
                try:
                    from models import LoanSummary, PaymentSchedule
                    
                    # Test table access
                    loan_count = LoanSummary.query.count()
                    schedule_count = PaymentSchedule.query.count()
                    
                    logger.info(f"✓ Loan calculator storage operational:")
                    logger.info(f"  - LoanSummary table: {loan_count} records")
                    logger.info(f"  - PaymentSchedule table: {schedule_count} records")
                    
                    return True
                    
                except Exception as storage_error:
                    logger.error(f"Loan calculator storage test failed: {storage_error}")
                    return False
            else:
                logger.error("Database connection test failed - no result returned")
                return False
                
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False

def create_required_directories():
    """Create required application directories"""
    directories = [
        'uploads',
        'static/uploads', 
        'instance',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Directory created/verified: {directory}")

def create_default_env():
    """Create default .env file if it doesn't exist"""
    env_path = '.env'
    if not os.path.exists(env_path):
        logger.info("Creating default .env file...")
        env_content = """# Novellus Loan Management System Environment Configuration
SESSION_SECRET=novellus-loan-management-secret-key-2025-change-this-in-production
DATABASE_URL=sqlite:///novellus_loans.db
FLASK_ENV=development
FLASK_DEBUG=True
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
SQLALCHEMY_TRACK_MODIFICATIONS=False
SQLALCHEMY_ENGINE_OPTIONS={"pool_recycle": 300, "pool_pre_ping": True}
"""
        with open(env_path, 'w') as f:
            f.write(env_content)
        logger.info(f"Default .env file created: {env_path}")
    else:
        logger.info(".env file already exists")

if __name__ == '__main__':
    logger.info("="*60)
    logger.info("Novellus Loan Management System - Database Initialization")
    logger.info("Including Loan Calculator Data Storage Setup")
    logger.info("="*60)
    
    # Create required directories
    create_required_directories()
    
    # Create default environment file
    create_default_env()
    
    # Initialize database with loan calculator storage
    if init_database():
        # Test database connection and loan calculator storage
        if test_database_connection():
            logger.info("="*60)
            logger.info("✓ Database setup completed successfully!")
            logger.info("✓ Loan calculator data storage is ready")
            logger.info("✓ System ready to store and retrieve loan calculations")
            logger.info("="*60)
            sys.exit(0)
        else:
            logger.error("Database connection or loan calculator storage test failed")
            sys.exit(1)
    else:
        logger.error("Database initialization failed")
        sys.exit(1)