import os
import json
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify, session, send_file, make_response
from flask_login import login_user, logout_user, login_required, current_user
from flask_cors import cross_origin
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import tempfile

from app import app, db
from models import User, Application, Quote, Document, Payment, Communication, LoanSummary, PaymentSchedule
import sqlalchemy as sa
from calculations import LoanCalculator
# Import PDF and Excel generators
from pdf_quote_generator import generate_quote_pdf, generate_professional_quote_docx
from excel_generator import NovellussExcelGenerator
# BIRT integration removed for simplified on-premise deployment
from utils import (
    allowed_file, secure_upload_filename, validate_loan_application_data,
    validate_quote_data, generate_payment_schedule_csv, format_currency,
    parse_currency_amount, generate_application_reference, validate_email
)

# Import Power BI and Scenario Comparison modules
try:
    from powerbi_final_working_refresh import FinalWorkingPowerBIRefresher
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    POWERBI_AVAILABLE = True
    app.logger.info("Power BI refresh module loaded successfully")
except ImportError as e:
    app.logger.warning(f"Power BI refresh module not available: {str(e)}")
    POWERBI_AVAILABLE = False

from scenario_comparison import ScenarioComparison, ScenarioTemplates, create_scenario_comparison_from_request
import threading
import asyncio
from datetime import datetime
import json

# Initialize Power BI scheduler if available
if POWERBI_AVAILABLE:
    try:
        # Initialize global scheduler
        scheduler = BackgroundScheduler()
        scheduler.start()
        scheduler_active = False
        _global_scheduler = None
        app.logger.info("Power BI scheduler initialized successfully")
        
        # Load and restore saved schedule configuration
        def load_and_restore_schedule():
            try:
                schedule_config_file = 'powerbi_schedule_config.json'
                if os.path.exists(schedule_config_file):
                    with open(schedule_config_file, 'r') as f:
                        config = json.load(f)
                    
                    if config.get('enabled', False):
                        username = config.get('username')
                        password = config.get('password')
                        dataset_url = config.get('dataset_url')
                        interval = config.get('interval', 60)
                        
                        if all([username, password, dataset_url]):
                            # Create scheduled refresh function
                            def scheduled_refresh():
                                try:
                                    app.logger.info("Starting persistent scheduled Power BI refresh...")
                                    refresher = FinalWorkingPowerBIRefresher(username, password, dataset_url)
                                    success = refresher.refresh_dataset_final()
                                    app.logger.info(f"Persistent scheduled Power BI refresh completed: {success}")
                                except Exception as e:
                                    app.logger.error(f"Persistent scheduled Power BI refresh error: {str(e)}")
                            
                            # Schedule the job
                            scheduler.add_job(
                                scheduled_refresh,
                                trigger=IntervalTrigger(minutes=interval),
                                id='powerbi_refresh',
                                replace_existing=True
                            )
                            
                            global scheduler_active
                            scheduler_active = True
                            app.logger.info(f"Restored Power BI schedule from config: every {interval} minutes")
                        else:
                            app.logger.warning("Incomplete schedule configuration found - skipping restore")
                    else:
                        app.logger.info("Saved schedule configuration is disabled")
                else:
                    app.logger.info("No saved schedule configuration found")
            except Exception as e:
                app.logger.error(f"Failed to restore Power BI schedule: {str(e)}")
        
        # Restore schedule after a short delay to ensure everything is initialized
        import threading
        threading.Timer(2.0, load_and_restore_schedule).start()
        
    except Exception as e:
        app.logger.error(f"Failed to initialize Power BI scheduler: {str(e)}")
        scheduler = None
        scheduler_active = False
        _global_scheduler = None
else:
    scheduler = None
    scheduler_active = False
    _global_scheduler = None

# Safe conversion utility functions
def safe_float(value, default=0.0):
    """Safely convert value to float, handling empty strings and None values"""
    if value is None or value == '' or value == 'null':
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        app.logger.warning(f"Could not convert '{value}' to float, using default {default}")
        return default

def safe_int(value, default=0):
    """Safely convert value to int, handling empty strings and None values"""
    if value is None or value == '' or value == 'null':
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        app.logger.warning(f"Could not convert '{value}' to int, using default {default}")
        return default

# Date parsing utility function
def parse_payment_date_flexible(payment_date_str):
    """Parse payment date with flexible format support (DD/MM/YYYY or YYYY-MM-DD)"""
    if not payment_date_str:
        return datetime.now().date()
    
    # Try DD/MM/YYYY format first (most common from calculations)
    try:
        return datetime.strptime(payment_date_str, '%d/%m/%Y').date()
    except ValueError:
        # Try YYYY-MM-DD format as fallback
        try:
            return datetime.strptime(payment_date_str, '%Y-%m-%d').date()
        except ValueError:
            app.logger.warning(f"Could not parse payment date '{payment_date_str}', using current date")
            return datetime.now().date()

# Initialize calculator and quote generator
calculator = LoanCalculator()
# BIRT integration removed for simplified deployment

# Initialize Working Report Generator (reliable alternative)
try:
    from simple_report_generator import working_report_generator
    app.logger.info("Working Report Generator loaded successfully")
except ImportError as e:
    working_report_generator = None
    app.logger.warning(f"Working Report Generator not available: {e}")

@app.route('/')
def index():
    """Main landing page - redirect to calculator"""
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        role = request.form['role']
        phone = request.form.get('phone', '')
        company = request.form.get('company', '')
        
        # Validation
        errors = []
        
        if not validate_email(email):
            errors.append('Please enter a valid email address')
        
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered')
        
        if len(password) < 6:
            errors.append('Password must be at least 6 characters')
        
        if password != confirm_password:
            errors.append('Passwords do not match')
        
        if not first_name or not last_name:
            errors.append('First name and last name are required')
        
        if role not in ['borrower', 'lender']:
            errors.append('Please select a valid role')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            phone=phone,
            company=company
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    if current_user.role == 'borrower':
        # Borrower dashboard - show their applications
        applications = Application.query.filter_by(user_id=current_user.id).order_by(Application.created_at.desc()).all()
        quotes = Quote.query.join(Application).filter(Application.user_id == current_user.id).order_by(Quote.created_at.desc()).limit(5).all()
        payments = Payment.query.join(Application).filter(Application.user_id == current_user.id).order_by(Payment.created_at.desc()).limit(5).all()
        
    else:
        # Lender dashboard - show all applications
        applications = Application.query.order_by(Application.created_at.desc()).limit(10).all()
        quotes = Quote.query.order_by(Quote.created_at.desc()).limit(5).all()
        payments = Payment.query.order_by(Payment.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         applications=applications, 
                         quotes=quotes, 
                         payments=payments)

@app.route('/calculator')
def calculator_page():
    """Loan calculator page"""
    return render_template('calculator.html')

@app.route('/api/calculate', methods=['POST'])
def api_calculate():
    """API endpoint for loan calculations"""
    # Clear previous calculation hash to allow new calculations
    if 'last_calc_hash' in session:
        del session['last_calc_hash']
        session.modified = True
        
    try:
        data = request.get_json()
        
        # Extract parameters
        loan_type = data.get('loan_type', 'bridge')
        repayment_option = data.get('repayment_option', 'none')
        currency = data.get('currency', 'GBP')
        
        # Property and loan details - using safe conversion
        property_value = safe_float(data.get('property_value'), 0)
        
        # Handle gross/net amount input
        amount_input_type = data.get('amount_input_type', 'gross')
        if amount_input_type == 'gross':
            if data.get('gross_amount_type') == 'percentage':
                gross_amount = property_value * (safe_float(data.get('gross_amount_percentage'), 0) / 100)
            else:
                gross_amount = safe_float(data.get('gross_amount'), 0)
        else:
            # Net amount input - calculate gross
            net_amount = safe_float(data.get('net_amount'), 0)
            # This will be handled by the conversion function
            gross_amount = net_amount  # Temporary, will be calculated
        
        # Interest rate handling - CRITICAL FIX: Support both field names
        rate_input_type = data.get('rate_input_type', 'annual')  # Default to annual, not monthly
        if rate_input_type == 'annual':
            # Support both 'annual_rate' and 'interest_rate' field names
            annual_rate = safe_float(data.get('annual_rate'), 0) or safe_float(data.get('interest_rate'), 0)
            monthly_rate = annual_rate / 12 if annual_rate > 0 else 0
        else:
            monthly_rate = safe_float(data.get('monthly_rate'), 0)
            annual_rate = monthly_rate * 12 if monthly_rate > 0 else 0
            
        # Debug logging to see what's being passed
        import logging
        logging.info(f"Routes - Interest rate extraction: rate_input_type={rate_input_type}, annual_rate={annual_rate}, monthly_rate={monthly_rate}")
        
        # Other parameters - using safe conversion
        loan_term = safe_int(data.get('loan_term'), 12)
        start_date_str = data.get('start_date', datetime.now().strftime('%Y-%m-%d'))
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        
        # Handle end date - if provided, pass it to calculation engine
        end_date_str = data.get('end_date')
        if end_date_str and end_date_str.strip():
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                # Calculate loan term based on actual dates for parameter passing
                months_diff = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                if months_diff > 0:
                    loan_term = months_diff
            except ValueError:
                app.logger.warning(f"Could not parse end date '{end_date_str}', ignoring")
                end_date_str = None
        else:
            end_date_str = None
        
        # Fees - using safe conversion
        arrangement_fee_rate = safe_float(data.get('arrangement_fee_percentage'), 0) # Frontend sends 'arrangement_fee_percentage'
        legal_fees = safe_float(data.get('legal_fees'), 0)
        site_visit_fee = safe_float(data.get('site_visit_fee'), 0)
        title_insurance_rate = safe_float(data.get('title_insurance_rate'), 0)
        
        # Additional parameters for specific loan types - using safe conversion
        capital_repayment = safe_float(data.get('capital_repayment'), 0)
        flexible_payment = safe_float(data.get('flexible_payment'), 0)
        
        # Handle development loan tranches - CRITICAL FIX for user tranche input
        tranches = data.get('tranches', data.get('user_tranches', []))
        
        # Debug logging to see what tranches data we received
        import logging
        logging.info(f"ROUTES.PY TRANCHE DEBUG: Received {len(tranches)} tranches from API request")
        if tranches:
            for i, tranche in enumerate(tranches[:3]):  # Show first 3 for debugging
                logging.info(f"  Tranche {i+1}: Amount=£{tranche.get('amount', 0):,.2f}, Date={tranche.get('date', 'N/A')}")
        
        # Day 1 advance for development loans - using safe conversion
        day1_advance = safe_float(data.get('day1_advance'), 0)
        
        # Daily rate calculation method
        use_360_days = data.get('use_360_days') == 'true'  # Convert string to boolean
        app.logger.info(f"ROUTES.PY DEBUG: use_360_days parameter = {use_360_days} (from {data.get('use_360_days')})")
        
        # Build parameters dictionary
        calc_params = {
            'loan_type': loan_type,
            'repayment_option': repayment_option,
            'property_value': property_value,
            'gross_amount': gross_amount,
            'annual_rate': annual_rate,
            'monthly_rate': monthly_rate,
            'loan_term': loan_term,
            'start_date': start_date_str,  # Pass as string, not datetime object
            'end_date': end_date_str,  # Add end date parameter
            'arrangement_fee_rate': arrangement_fee_rate,
            'legal_fees': legal_fees,
            'site_visit_fee': site_visit_fee,
            'title_insurance_rate': title_insurance_rate,
            'capital_repayment': capital_repayment,
            'flexible_payment': flexible_payment,
            'currency': currency,
            'tranches': tranches,
            'day1_advance': day1_advance,
            'amount_input_type': amount_input_type,  # Add missing parameter
            'interest_type': data.get('interest_type', 'simple'),
            'payment_timing': data.get('payment_timing', 'advance'),
            'payment_frequency': data.get('payment_frequency', 'monthly'),
            'use_360_days': use_360_days  # Add the new daily rate calculation parameter
        }
        
        # Handle net-to-gross conversion if needed
        if amount_input_type == 'net':
            calc_params['net_amount'] = net_amount
        
        # Use the unified calculation method
        result = calculator.calculate_loan(calc_params)
        
        # Generate payment schedule
        try:
            # Add the original parameters to the result for payment schedule generation
            result['loan_type'] = loan_type
            result['repayment_option'] = repayment_option
            currency_symbol = '€' if currency == 'EUR' else '£'
            payment_schedule = calculator.generate_payment_schedule(result, currency_symbol)
            result['payment_schedule'] = payment_schedule
        except Exception as e:
            app.logger.warning(f"Payment schedule generation failed: {str(e)}")
            result['payment_schedule'] = []
        
        # Add currency symbol and additional fields needed for PDF generation
        result['currency'] = currency
        result['currency_symbol'] = '£' if currency == 'GBP' else '€'
        
        # CRITICAL: Preserve user input Day 1 Advance for display purposes
        result['userInputDay1Advance'] = day1_advance
        
        # Ensure all required fields are present for PDF generation
        if 'gross_amount' in result and 'grossAmount' not in result:
            result['grossAmount'] = result['gross_amount']
        if 'total_interest' in result and 'totalInterest' not in result:
            result['totalInterest'] = result['total_interest']
        if 'arrangement_fee' in result and 'arrangementFee' not in result:
            result['arrangementFee'] = result['arrangement_fee']
        if 'net_advance' in result and 'netAdvance' not in result:
            result['netAdvance'] = result['net_advance']
        
        # Calculate Total Net Advance = Gross Amount - Arrangement Fees - Legal Costs - Site Visit Fee - Title Insurance
        gross_amount_value = result.get('grossAmount', result.get('gross_amount', 0))
        arrangement_fee_value = result.get('arrangementFee', result.get('arrangement_fee', 0))
        
        # Calculate individual fee components
        # CRITICAL FIX: Title insurance should be calculated on Gross Amount, not Property Value
        # title_insurance_rate is already in percentage form (0.1 = 0.1%), so divide by 100
        title_insurance_value = gross_amount_value * (title_insurance_rate / 100)
        total_legal_costs = legal_fees + title_insurance_value
        
        # Total Net Advance calculation depends on repayment type
        # For retained interest repayment types: Gross Amount - All Fees - Interest  
        # For non-retained repayment types: Gross Amount - All Fees (no interest deduction)
        total_interest_value = result.get('totalInterest', result.get('total_interest', 0))
        loan_type = result.get('loan_type', '')
        repayment_option = calc_params.get('repayment_option', 'none')
        
        # CRITICAL FIX: For development loans, Total Net Advance should equal the user's net amount input
        if loan_type == 'development' or loan_type == 'development2':
            # Development loans: Total Net Advance = User's net amount input (always £800,000)
            total_net_advance = calc_params.get('net_amount', net_amount)
            app.logger.info(f'ROUTES.PY {loan_type.upper()} LOAN NET ADVANCE: Using user input net amount = £{total_net_advance:.2f}')
        else:
            # Bridge/term loans: Calculate based on repayment type
            is_retained_interest = repayment_option == 'none' or repayment_option == 'capital_payment_only'  # Bridge/term loans with retained interest repayment
            
            if is_retained_interest:
                # Retained interest: deduct interest from net advance
                # For capital_payment_only, use retainedInterest (full amount) instead of totalInterest (net after refund)
                if repayment_option == 'capital_payment_only':
                    interest_for_net_advance = result.get('retainedInterest', total_interest_value)
                    app.logger.info(f'ROUTES.PY CAPITAL PAYMENT ONLY: Using retainedInterest £{interest_for_net_advance:.2f} instead of totalInterest £{total_interest_value:.2f}')
                else:
                    # CRITICAL FIX: For bridge/term loans with Net-to-Gross Excel formula, use Excel-calculated interest
                    amount_input_type = calc_params.get('amount_input_type', 'gross')
                    if amount_input_type == 'net' and loan_type in ['bridge', 'term']:
                        # Calculate Excel interest: (Gross × Rate × Months/12) / 100
                        annual_rate = calc_params.get('annual_rate', 0)
                        loan_term = calc_params.get('loan_term', 12)
                        excel_interest = (gross_amount_value * annual_rate * loan_term) / (12 * 100)
                        interest_for_net_advance = excel_interest
                        
                        # CRITICAL FIX: Update the totalInterest field in result to use Excel interest
                        result['totalInterest'] = excel_interest
                        result['total_interest'] = excel_interest  # Also update snake_case version for consistency
                        
                        app.logger.info(f'ROUTES.PY EXCEL NET-TO-GROSS ({loan_type}): Using Excel interest £{excel_interest:.2f} = (£{gross_amount_value:.2f} × {annual_rate}% × {loan_term}/12)/100 instead of calculation engine £{total_interest_value:.2f}')
                        app.logger.info(f'ROUTES.PY EXCEL NET-TO-GROSS ({loan_type}): Updated result totalInterest field to £{excel_interest:.2f}')
                    else:
                        interest_for_net_advance = total_interest_value
                
                total_net_advance = gross_amount_value - arrangement_fee_value - legal_fees - site_visit_fee - title_insurance_value - interest_for_net_advance
                app.logger.info(f'ROUTES.PY RETAINED INTEREST NET ADVANCE ({loan_type}): £{gross_amount_value:.2f} - £{arrangement_fee_value:.2f} - £{legal_fees:.2f} - £{site_visit_fee:.2f} - £{title_insurance_value:.2f} - £{interest_for_net_advance:.2f} = £{total_net_advance:.2f}')
            else:
                # For service only (interest payments): calculation depends on input type and payment timing
                if repayment_option == 'service_only':
                    amount_input_type = calc_params.get('amount_input_type', 'gross')
                    if amount_input_type == 'net' and loan_type in ['bridge', 'term']:
                        # Net-to-Gross: Total Net Advance should equal the user's net input
                        user_net_amount = calc_params.get('net_amount', calc_params.get('gross_amount', 0))
                        total_net_advance = user_net_amount
                        app.logger.info(f'ROUTES.PY EXCEL NET-TO-GROSS ({loan_type}, service_only): Total Net Advance = user input £{total_net_advance:.2f}')
                    else:
                        # For Gross-to-Net calculations: Check payment timing to determine correct calculation
                        payment_timing = calc_params.get('payment_timing', 'advance')
                        
                        if payment_timing == 'advance':
                            # Paid in advance: Total Net Advance = Gross Amount - First Period Interest - All Fees
                            first_period_interest = result.get('firstPeriodInterest', result.get('monthlyPayment', 0))
                            total_net_advance = gross_amount_value - first_period_interest - arrangement_fee_value - legal_fees - site_visit_fee - title_insurance_value
                            app.logger.info(f'ROUTES.PY SERVICE ONLY ADVANCE NET ADVANCE ({loan_type}): £{gross_amount_value:.2f} - £{first_period_interest:.2f} (first period interest) - £{arrangement_fee_value:.2f} - £{legal_fees:.2f} - £{site_visit_fee:.2f} - £{title_insurance_value:.2f} = £{total_net_advance:.2f}')
                        else:
                            # Paid in arrears: Total Net Advance = Gross Amount - All Fees
                            total_net_advance = gross_amount_value - arrangement_fee_value - legal_fees - site_visit_fee - title_insurance_value
                            app.logger.info(f'ROUTES.PY SERVICE ONLY ARREARS NET ADVANCE ({loan_type}): £{gross_amount_value:.2f} - £{arrangement_fee_value:.2f} - £{legal_fees:.2f} - £{site_visit_fee:.2f} - £{title_insurance_value:.2f} = £{total_net_advance:.2f}')
                else:
                    # CRITICAL FIX: For Net-to-Gross calculations with non-retained repayment options, 
                    # the Excel formulas already account for the correct relationship between Net and Gross
                    amount_input_type = calc_params.get('amount_input_type', 'gross')
                    if amount_input_type == 'net' and loan_type in ['bridge', 'term']:
                        # Net-to-Gross: Total Net Advance should equal the user's net input
                        user_net_amount = calc_params.get('net_amount', calc_params.get('gross_amount', 0))
                        total_net_advance = user_net_amount
                        app.logger.info(f'ROUTES.PY EXCEL NET-TO-GROSS ({loan_type}, {repayment_option}): Total Net Advance = user input £{total_net_advance:.2f}')
                    else:
                        # For Gross-to-Net calculations: Total Net Advance = Gross Amount - All Fees (no interest deduction)
                        total_net_advance = gross_amount_value - arrangement_fee_value - legal_fees - site_visit_fee - title_insurance_value
                        app.logger.info(f'ROUTES.PY {repayment_option.upper()} NET ADVANCE ({loan_type}): £{gross_amount_value:.2f} - £{arrangement_fee_value:.2f} - £{legal_fees:.2f} - £{site_visit_fee:.2f} - £{title_insurance_value:.2f} = £{total_net_advance:.2f}')
            
        # NO ROUNDING - maintain exact precision
        result['totalNetAdvance'] = float(total_net_advance)
        
        # Store individual fee components for display (no rounding)
        result['siteVisitFee'] = float(site_visit_fee)
        result['titleInsurance'] = float(title_insurance_value)
        result['legalCosts'] = float(legal_fees)
        result['totalLegalCosts'] = float(total_legal_costs)
        
        # NO ROUNDING - maintain exact precision for all financial results
        if 'grossAmount' in result:
            result['grossAmount'] = float(result['grossAmount'])
        if 'totalInterest' in result:
            result['totalInterest'] = float(result['totalInterest'])
        if 'arrangementFee' in result:
            result['arrangementFee'] = float(result['arrangementFee'])
        if 'netAdvance' in result:
            result['netAdvance'] = float(result['netAdvance'])
        if 'periodicInterest' in result:
            result['periodicInterest'] = float(result['periodicInterest'])
        if 'total_legal_fees' in result and 'totalLegalFees' not in result:
            result['totalLegalFees'] = result['total_legal_fees']
        if 'property_value' in result and 'propertyValue' not in result:
            result['propertyValue'] = result['property_value']
        if 'interest_rate' in result and 'interestRate' not in result:
            result['interestRate'] = result['interest_rate']
        if 'loan_term' in result and 'loanTerm' not in result:
            result['loanTerm'] = result['loan_term']
        # Add currency symbol field mapping for DOCX generation
        if 'currency_symbol' in result and 'currencySymbol' not in result:
            result['currencySymbol'] = result['currency_symbol']
        
        # Store minimal essential data in session to avoid cookie size limit
        essential_data = {
            'loan_type': result.get("loan_type"),
            'grossAmount': result.get("grossAmount"),
            'totalInterest': result.get("totalInterest"),
            'arrangementFee': result.get("arrangementFee"),
            'netAdvance': result.get("netAdvance"),
            'totalNetAdvance': result.get("totalNetAdvance"),
            'currency': result.get('currency', 'GBP'),
            'calculation_timestamp': datetime.now().isoformat()
        }
        session['last_calculation_result'] = essential_data
        session.modified = True
        
        # Remove automatic loan storage - only save when user clicks save button
        # AUTOMATIC LOAN STORAGE REMOVED: Now only saves on manual save button click
        result['auto_saved'] = False
        
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Calculation error: {str(e)}")
        return jsonify({'error': 'Calculation failed'}), 500

@app.route('/api/monthly-breakdown', methods=['POST'])
def monthly_breakdown():
    """Generate detailed monthly compound daily interest breakdown for development loans"""
    try:
        data = request.get_json()
        
        # Extract parameters
        params = {
            'loan_type': 'development',
            'annual_rate': float(data.get('annual_rate', 12.0)),
            'loan_term': int(data.get('loan_term', 18)),
            'start_date': data.get('start_date', '2025-07-16'),
            'day1_advance': float(data.get('day1_advance', 100000)),
            'net_amount': float(data.get('net_amount', 0))
        }
        
        calculator = LoanCalculator()
        breakdown = calculator.generate_monthly_principal_breakdown(params)
        
        return jsonify({
            'success': True,
            'breakdown': breakdown,
            'summary': {
                'total_months': len(breakdown),
                'day1_advance': params['day1_advance'],
                'net_amount': params['net_amount'],
                'annual_rate': params['annual_rate'],
                'daily_rate': params['annual_rate'] / 365
            }
        })
        
    except Exception as e:
        app.logger.error(f'Monthly breakdown error: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/excel-style-breakdown', methods=['POST'])
def excel_style_breakdown():
    """Generate Excel-style tranche breakdown table matching the provided format"""
    try:
        data = request.get_json()
        
        # Extract parameters
        annual_rate = float(data.get('annual_rate', 12.0))
        loan_term = int(data.get('loan_term', 18))
        start_date_str = data.get('start_date', '2025-07-16')
        day1_advance = float(data.get('day1_advance', 100000))
        net_amount = float(data.get('net_amount', 0))
        
        # Parse start date
        from datetime import datetime
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        
        # Calculate daily rate
        daily_rate = annual_rate / 100 / 365
        
        # Calculate monthly tranche releases (progressive)
        remaining_amount = net_amount - day1_advance
        monthly_release = remaining_amount / (loan_term - 1) if loan_term > 1 else 0
        
        # Initialize table data
        table_rows = []
        
        # Track running balances
        current_balance = 0
        total_cumulative_interest = 0
        
        for month in range(1, loan_term + 1):
            # Calculate month dates
            current_date = start_date
            for _ in range(month - 1):
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
            
            # Get days in month (realistic)
            if current_date.month == 12:
                next_month = current_date.replace(year=current_date.year + 1, month=1)
            else:
                next_month = current_date.replace(month=current_date.month + 1)
            days_in_month = (next_month - current_date).days
            
            # Opening balance for this month
            opening_balance = current_balance
            
            # Monthly release amount
            if month == 1:
                monthly_release_amount = day1_advance
            elif month <= loan_term:
                if month == loan_term:
                    # Last month - release remaining amount
                    monthly_release_amount = net_amount - day1_advance - (monthly_release * (month - 2))
                else:
                    monthly_release_amount = monthly_release
            else:
                monthly_release_amount = 0
            
            # Add new tranche to balance
            balance_after_release = opening_balance + monthly_release_amount
            
            # Calculate compound daily interest for the month
            # Formula: Balance × (1 + daily_rate)^days_in_month - Balance
            if balance_after_release > 0:
                compound_factor = (1 + daily_rate) ** days_in_month
                end_balance = balance_after_release * compound_factor
                monthly_interest = end_balance - balance_after_release
            else:
                end_balance = 0
                monthly_interest = 0
            
            # Update running totals
            current_balance = end_balance
            total_cumulative_interest += monthly_interest
            
            # Create row with exact precision (no rounding)
            row = {
                'month': month,
                'date': current_date.strftime('%d-%b-%Y'),
                'opening_balance': opening_balance,
                'monthly_release': monthly_release_amount,
                'balance_after_release': balance_after_release,
                'days_in_month': days_in_month,
                'daily_rate': f"{daily_rate:.8f}",
                'daily_rate_percent': f"{daily_rate * 100:.6f}%",
                'compound_factor': compound_factor if balance_after_release > 0 else 1,
                'monthly_interest': monthly_interest,
                'end_period_balance': end_balance,
                'cumulative_interest': total_cumulative_interest,
                'calculation_formula': f"£{balance_after_release:,.2f} × (1 + {daily_rate:.8f})^{days_in_month}" if balance_after_release > 0 else "No balance"
            }
            
            table_rows.append(row)
        
        # Calculate totals
        total_releases = sum(row['monthly_release'] for row in table_rows)
        total_interest = table_rows[-1]['cumulative_interest'] if table_rows else 0
        final_balance = table_rows[-1]['end_period_balance'] if table_rows else 0
        
        return jsonify({
            'success': True,
            'table_data': table_rows,
            'summary': {
                'total_months': loan_term,
                'total_releases': total_releases,
                'total_interest': total_interest,
                'final_balance': final_balance,
                'day1_advance': day1_advance,
                'net_amount': net_amount,
                'annual_rate': annual_rate,
                'daily_rate': daily_rate
            }
        })
        
    except Exception as e:
        app.logger.error(f'Excel-style breakdown error: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/export-schedule', methods=['POST'])
@login_required
def api_export_schedule():
    """Export payment schedule as CSV"""
    try:
        data = request.get_json()
        schedule = data.get('schedule', [])
        currency = data.get('currency', 'GBP')
        loan_type = data.get('loan_type', 'bridge')
        
        csv_content = generate_payment_schedule_csv(schedule, currency)
        
        # Create response
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=payment_schedule_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return response
        
    except Exception as e:
        app.logger.error(f"Export error: {str(e)}")
        return jsonify({'error': 'Export failed'}), 500

@app.route('/applications')
@login_required
def applications():
    """Applications management page"""
    if current_user.role == 'borrower':
        apps = Application.query.filter_by(user_id=current_user.id).order_by(Application.created_at.desc()).all()
    else:
        apps = Application.query.order_by(Application.created_at.desc()).all()
    
    return render_template('applications.html', applications=apps)

@app.route('/applications/new', methods=['GET', 'POST'])
@login_required
def new_application():
    """Create new loan application"""
    if request.method == 'POST':
        # Extract form data
        data = {
            'loan_type': request.form['loan_type'],
            'loan_purpose': request.form.get('loan_purpose', ''),
            'property_address': request.form['property_address'],
            'property_type': request.form.get('property_type', ''),
            'property_value': request.form['property_value'],
            'loan_amount': request.form['loan_amount'],
            'loan_term': request.form['loan_term'],
            'monthly_income': request.form.get('monthly_income', ''),
            'annual_income': request.form.get('annual_income', ''),
            'existing_debt': request.form.get('existing_debt', ''),
            'credit_score': request.form.get('credit_score', '')
        }
        
        # Validate data
        errors = validate_loan_application_data(data)
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('application_form.html')
        
        # Create application
        application = Application(
            user_id=current_user.id,
            loan_type=data['loan_type'],
            loan_purpose=data['loan_purpose'],
            property_address=data['property_address'],
            property_type=data['property_type'],
            property_value=float(data['property_value']),
            loan_amount=float(data['loan_amount']),
            loan_term=int(data['loan_term']),
            monthly_income=float(data['monthly_income']) if data['monthly_income'] else None,
            annual_income=float(data['annual_income']) if data['annual_income'] else None,
            existing_debt=float(data['existing_debt']) if data['existing_debt'] else None,
            credit_score=int(data['credit_score']) if data['credit_score'] else None,
            status='draft'
        )
        
        # Calculate LTV
        application.ltv_ratio = (application.loan_amount / application.property_value) * 100
        
        db.session.add(application)
        db.session.commit()
        
        flash('Application created successfully!', 'success')
        return redirect(url_for('application_detail', id=application.id))
    
    return render_template('application_form.html')

@app.route('/applications/<int:id>')
@login_required
def application_detail(id):
    """View application details"""
    application = Application.query.get_or_404(id)
    
    # Check permissions
    if current_user.role == 'borrower' and application.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('applications'))
    
    quotes = Quote.query.filter_by(application_id=id).order_by(Quote.created_at.desc()).all()
    documents = Document.query.filter_by(application_id=id).order_by(Document.created_at.desc()).all()
    payments = Payment.query.filter_by(application_id=id).order_by(Payment.created_at.desc()).all()
    communications = Communication.query.filter_by(application_id=id).order_by(Communication.created_at.desc()).all()
    
    return render_template('application_detail.html', 
                         application=application,
                         quotes=quotes,
                         documents=documents,
                         payments=payments,
                         communications=communications)

@app.route('/applications/<int:id>/submit', methods=['POST'])
@login_required
def submit_application(id):
    """Submit application for review"""
    application = Application.query.get_or_404(id)
    
    # Check permissions
    if current_user.role == 'borrower' and application.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('applications'))
    
    if application.status == 'draft':
        application.status = 'submitted'
        application.submitted_at = datetime.utcnow()
        db.session.commit()
        flash('Application submitted successfully!', 'success')
    else:
        flash('Application has already been submitted', 'warning')
    
    return redirect(url_for('application_detail', id=id))

@app.route('/quotes')
@login_required
def quotes():
    """Quotes management page"""
    if current_user.role == 'borrower':
        user_quotes = Quote.query.join(Application).filter(Application.user_id == current_user.id).order_by(Quote.created_at.desc()).all()
    else:
        user_quotes = Quote.query.order_by(Quote.created_at.desc()).all()
    
    return render_template('quotes.html', quotes=user_quotes)

@app.route('/quotes/generate/<int:application_id>', methods=['GET', 'POST'])
@login_required
def generate_quote(application_id):
    """Generate quote for application"""
    if current_user.role != 'lender':
        flash('Access denied - lenders only', 'error')
        return redirect(url_for('applications'))
    
    application = Application.query.get_or_404(application_id)
    
    if request.method == 'POST':
        # Extract quote data
        data = {
            'gross_amount': request.form['gross_amount'],
            'net_amount': request.form['net_amount'],
            'interest_rate': request.form['interest_rate'],
            'loan_term': request.form['loan_term'],
            'arrangement_fee': request.form.get('arrangement_fee', 0),
            'legal_fees': request.form.get('legal_fees', 0),
            'valuation_fee': request.form.get('valuation_fee', 0),
            'title_insurance': request.form.get('title_insurance', 0),
            'exit_fee': request.form.get('exit_fee', 0),
            'monthly_payment': request.form['monthly_payment'],
            'total_interest': request.form['total_interest'],
            'total_amount': request.form['total_amount']
        }
        
        # Validate quote data
        errors = validate_quote_data(data)
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('quote_form.html', application=application)
        
        # Create quote
        quote = Quote(
            application_id=application_id,
            created_by=current_user.id,
            gross_amount=float(data['gross_amount']),
            net_amount=float(data['net_amount']),
            interest_rate=float(data['interest_rate']),
            loan_term=int(data['loan_term']),
            arrangement_fee=float(data['arrangement_fee']),
            legal_fees=float(data['legal_fees']),
            valuation_fee=float(data['valuation_fee']),
            title_insurance=float(data['title_insurance']),
            exit_fee=float(data['exit_fee']),
            monthly_payment=float(data['monthly_payment']),
            total_interest=float(data['total_interest']),
            total_amount=float(data['total_amount']),
            ltv_ratio=(float(data['gross_amount']) / application.property_value) * 100,
            valid_until=datetime.utcnow() + timedelta(days=30),
            status='draft'
        )
        
        db.session.add(quote)
        db.session.commit()
        
        flash('Quote generated successfully!', 'success')
        return redirect(url_for('quote_detail', id=quote.id))
    
    return render_template('quote_form.html', application=application)

@app.route('/quotes/<int:id>')
@login_required
def quote_detail(id):
    """View quote details"""
    quote = Quote.query.get_or_404(id)
    
    # Check permissions
    if current_user.role == 'borrower':
        if quote.application.user_id != current_user.id:
            flash('Access denied', 'error')
            return redirect(url_for('quotes'))
    
    return render_template('quote_detail.html', quote=quote)

@app.route('/quotes/<int:id>/generate-document', methods=['POST'])
@login_required
def generate_quote_document(id):
    """Generate quote document using Word template"""
    if current_user.role != 'lender':
        flash('Access denied - lenders only', 'error')
        return redirect(url_for('quotes'))
    
    quote = Quote.query.get_or_404(id)
    application = quote.application
    
    try:
        # Prepare loan data
        loan_data = {
            'loan_type': application.loan_type,
            'property_address': application.property_address,
            'property_value': float(application.property_value),
            'gross_amount': float(quote.gross_amount),
            'net_advance': float(quote.net_amount),
            'interest_rate': float(quote.interest_rate),
            'loan_term': quote.loan_term,
            'ltv': float(quote.ltv_ratio),
            'arrangement_fee': float(quote.arrangement_fee),
            'legal_fees': float(quote.legal_fees),
            'valuation_fee': float(quote.valuation_fee),
            'title_insurance': float(quote.title_insurance),
            'total_legal_fees': float(quote.legal_fees + quote.title_insurance),
            'monthly_payment': float(quote.monthly_payment),
            'total_interest': float(quote.total_interest),
            'total_amount': float(quote.total_amount),
            'currency': 'GBP',  # Default to GBP for now
            'borrower_name': application.user.full_name
        }
        
        # Prepare borrower data
        borrower_data = {
            'first_name': application.user.first_name,
            'last_name': application.user.last_name,
            'email': application.user.email,
            'phone': application.user.phone or '',
            'company': application.user.company or '',
            'address': application.property_address
        }
        
        # Generate quote document as PDF
        pdf_content = generate_quote_pdf(loan_data, borrower_data)
        
        # Create response
        response = make_response(pdf_content)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=quote_{quote.id}.pdf'
        
        return response
        
    except Exception as e:
        app.logger.error(f"Quote generation error: {str(e)}")
        flash('Failed to generate quote document', 'error')
        return redirect(url_for('quote_detail', id=id))

@app.route('/api/generate-pdf-quote', methods=['POST'])
def api_generate_pdf_quote():
    """Generate PDF quote from calculator data"""
    try:
        data = request.get_json()
        
        # Extract calculation data and application data
        calculation_data = data.get('calculation_data', {})
        application_data = data.get('application_data', {})
        
        # Convert calculation data to quote format
        quote_data = {
            'id': datetime.now().strftime('%Y%m%d%H%M%S'),
            'gross_amount': calculation_data.get('grossAmount', calculation_data.get('gross_amount', 0)),
            'net_advance': calculation_data.get('netAdvance', calculation_data.get('net_advance', 0)),
            'interest_rate': calculation_data.get('interestRate', calculation_data.get('annual_rate', 0)),
            'loan_term': calculation_data.get('loanTerm', calculation_data.get('loan_term', 0)),
            'monthly_payment': calculation_data.get('monthlyPayment', calculation_data.get('monthly_payment', 0)),
            'total_interest': calculation_data.get('totalInterest', calculation_data.get('total_interest', 0)),
            'ltv_ratio': calculation_data.get('ltv', 0),
            'arrangement_fee': calculation_data.get('arrangementFee', calculation_data.get('arrangement_fee', 0)),
            'legal_fees': calculation_data.get('legalFees', calculation_data.get('legal_fees', 0)),
            'site_visit_fee': calculation_data.get('siteVisitFee', calculation_data.get('site_visit_fee', 0)),
            'valuation_fee': calculation_data.get('valuationFee', calculation_data.get('valuation_fee', 0)),
            'title_insurance': calculation_data.get('titleInsurance', calculation_data.get('title_insurance', 0)),
            'property_value': calculation_data.get('property_value', 0),
            'payment_schedule': calculation_data.get('payment_schedule', []),
            'currency': calculation_data.get('currency', 'GBP'),
            'currency_symbol': calculation_data.get('currency_symbol', '£')
        }
        
        # Generate PDF
        pdf_content = generate_quote_pdf(quote_data, application_data)
        
        # Create response
        response = make_response(pdf_content)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=novellus_quote_{quote_data["id"]}.pdf'
        
        return response
        
    except Exception as e:
        app.logger.error(f"PDF generation error: {str(e)}")
        return jsonify({'error': 'PDF generation failed'}), 500

@app.route('/api/generate-excel-quote', methods=['POST'])
@cross_origin(origins=['http://localhost:3000', 'https://novellus-loan-dashboard.replit.app'], 
             methods=['POST'], 
             supports_credentials=True
)
def api_generate_excel_quote():
    """Generate Excel quote from calculator data with Novellus branding"""
    try:
        data = request.get_json()
        
        # Extract calculation data and application data
        calculation_data = data.get('calculation_data', {})
        application_data = data.get('application_data', {})
        
        # Convert calculation data to quote format
        quote_data = {
            'id': datetime.now().strftime('%Y%m%d%H%M%S'),
            'gross_amount': calculation_data.get('grossAmount', calculation_data.get('gross_amount', 0)),
            'net_advance': calculation_data.get('netAdvance', calculation_data.get('net_advance', 0)),
            'interest_rate': calculation_data.get('interestRate', calculation_data.get('annual_rate', 0)),
            'loan_term': calculation_data.get('loanTerm', calculation_data.get('loan_term', 0)),
            'monthly_payment': calculation_data.get('monthlyPayment', calculation_data.get('monthly_payment', 0)),
            'total_interest': calculation_data.get('totalInterest', calculation_data.get('total_interest', 0)),
            'ltv_ratio': calculation_data.get('ltv', 0),
            'arrangement_fee': calculation_data.get('arrangementFee', calculation_data.get('arrangement_fee', 0)),
            'legal_fees': calculation_data.get('legalFees', calculation_data.get('legal_fees', 0)),
            'site_visit_fee': calculation_data.get('siteVisitFee', calculation_data.get('site_visit_fee', 0)),
            'title_insurance': calculation_data.get('titleInsurance', calculation_data.get('title_insurance', 0)),
            'property_value': calculation_data.get('property_value', 0),
            'payment_schedule': calculation_data.get('payment_schedule', []),
            'currency': calculation_data.get('currency', 'GBP'),
            'currency_symbol': calculation_data.get('currency_symbol', '£')
        }
        
        # Generate Excel
        excel_gen = NovellussExcelGenerator()
        excel_content = excel_gen.generate_quote_excel(quote_data, application_data)
        
        # Create response
        response = make_response(excel_content)
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename=novellus_quote_{quote_data["id"]}.xlsx'
        
        return response
        
    except Exception as e:
        app.logger.error(f"Excel generation error: {str(e)}")
        return jsonify({'error': 'Excel generation failed'}), 500

@app.route('/quotes/<int:id>/download-pdf')
@login_required
def download_quote_pdf(id):
    """Download PDF version of an existing quote"""
    try:
        quote = Quote.query.get_or_404(id)
        
        # Check permissions
        if current_user.role == 'borrower':
            application = Application.query.get(quote.application_id)
            if application.user_id != current_user.id:
                flash('Access denied', 'error')
                return redirect(url_for('dashboard'))
        
        # Prepare quote data
        quote_data = {
            'id': quote.id,
            'gross_amount': float(quote.gross_amount),
            'net_advance': float(quote.net_advance),
            'interest_rate': float(quote.interest_rate),
            'loan_term': quote.loan_term,
            'monthly_payment': float(quote.monthly_payment),
            'total_interest': float(quote.total_interest),
            'ltv_ratio': float(quote.ltv_ratio),
            'arrangement_fee': float(quote.arrangement_fee),
            'legal_fees': float(quote.legal_fees),
            'valuation_fee': float(quote.valuation_fee),
            'title_insurance': float(quote.title_insurance),
            'property_value': float(quote.application.property_value),
        }
        
        # Prepare application data
        application_data = {
            'loan_type': quote.application.loan_type,
            'loan_purpose': quote.application.loan_purpose,
            'property_address': quote.application.property_address,
            'user': {
                'first_name': quote.application.user.first_name,
                'last_name': quote.application.user.last_name,
                'email': quote.application.user.email,
                'phone': quote.application.user.phone or '',
                'company': quote.application.user.company or ''
            }
        }
        
        # Generate payment schedule if needed
        calculator_params = {
            'gross_amount': float(quote.gross_amount),
            'annual_rate': float(quote.interest_rate),
            'loan_term': quote.loan_term,
            'start_date': quote.application.created_at,
            'arrangement_fee_rate': 0,
            'legal_fees': 0,
            'site_visit_fee': 0,
            'title_insurance_rate': 0
        }
        
        if quote.application.loan_type == 'bridge':
            schedule_result = calculator.calculate_bridge_loan_retained_interest(calculator_params)
        elif quote.application.loan_type == 'term':
            schedule_result = calculator.calculate_term_loan_interest_only(calculator_params)
        else:
            schedule_result = {'payment_schedule': []}
        
        quote_data['payment_schedule'] = schedule_result.get('payment_schedule', [])
        
        # Generate PDF
        pdf_content = generate_quote_pdf(quote_data, application_data)
        
        # Create response
        response = make_response(pdf_content)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=novellus_quote_{quote.id}.pdf'
        
        return response
        
    except Exception as e:
        app.logger.error(f"PDF download error: {str(e)}")
        flash('Failed to generate PDF quote', 'error')
        return redirect(url_for('quote_detail', id=id))

@app.route('/payments')
@login_required
def payments():
    """Payments management page"""
    if current_user.role == 'borrower':
        user_payments = Payment.query.join(Application).filter(Application.user_id == current_user.id).order_by(Payment.created_at.desc()).all()
    else:
        user_payments = Payment.query.order_by(Payment.created_at.desc()).all()
    
    return render_template('payments.html', payments=user_payments)

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    """Handle file uploads"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        # Generate secure filename
        filename = secure_upload_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save file
        file.save(filepath)
        
        # Create document record
        document = Document(
            user_id=current_user.id,
            application_id=request.form.get('application_id'),
            filename=filename,
            original_filename=file.filename,
            file_path=filepath,
            file_size=os.path.getsize(filepath),
            mime_type=file.content_type,
            document_type=request.form.get('document_type', 'other')
        )
        
        db.session.add(document)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'document_id': document.id,
            'filename': filename,
            'original_filename': file.filename
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    """Serve uploaded files"""
    # Check if user has permission to view this file
    document = Document.query.filter_by(filename=filename).first_or_404()
    
    if current_user.role == 'borrower' and document.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    return send_file(document.file_path)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

def perform_fresh_calculation_for_download(form_data):
    """Perform fresh calculation for document downloads to ensure currency symbols are correct"""
    try:
        from calculations import LoanCalculator
        
        calculator = LoanCalculator()
        
        # Extract parameters from form data
        loan_type = form_data.get('loan_type', 'bridge')
        currency = form_data.get('currency', 'GBP')
        
        # Handle gross/net amount input
        amount_input_type = form_data.get('amount_input_type', 'gross')
        if amount_input_type == 'gross':
            if form_data.get('gross_amount_type') == 'percentage':
                property_value = float(form_data.get('property_value', 0))
                gross_amount = property_value * (float(form_data.get('gross_amount_percentage', 0)) / 100)
            else:
                gross_amount = float(form_data.get('gross_amount', 0))
        else:
            gross_amount = float(form_data.get('net_amount', 0))  # Will be converted
        
        # Interest rate handling
        rate_input_type = form_data.get('rate_input_type', 'annual')
        if rate_input_type == 'annual':
            annual_rate = float(form_data.get('annual_rate', 0))
        else:
            monthly_rate = float(form_data.get('monthly_rate', 0))
            annual_rate = monthly_rate * 12
        
        # Other parameters
        loan_term = int(form_data.get('loan_term', 12))
        start_date_str = form_data.get('start_date', datetime.now().strftime('%Y-%m-%d'))
        
        # Fees
        arrangement_fee_rate = float(form_data.get('arrangement_fee_rate', 0))
        legal_fees = float(form_data.get('legal_fees', 0))
        site_visit_fee = float(form_data.get('site_visit_fee', 0))
        title_insurance_rate = float(form_data.get('title_insurance_rate', 0))
        
        # Build calculation parameters
        calc_params = {
            'loan_type': loan_type,
            'gross_amount': gross_amount,
            'annual_rate': annual_rate,
            'loan_term': loan_term,
            'start_date': start_date_str,
            'arrangement_fee_rate': arrangement_fee_rate,
            'legal_fees': legal_fees,
            'site_visit_fee': site_visit_fee,
            'title_insurance_rate': title_insurance_rate,
            'currency': currency,
            'amount_input_type': amount_input_type,
            'interest_type': form_data.get('interest_type', 'simple'),
            'payment_timing': form_data.get('payment_timing', 'advance'),
            'payment_frequency': form_data.get('payment_frequency', 'monthly')
        }
        
        # Perform calculation
        result = calculator.calculate_loan(calc_params)
        
        # Generate payment schedule with proper currency symbol
        try:
            # Add the original parameters to the result for payment schedule generation
            result['loan_type'] = loan_type
            result['repayment_option'] = form_data.get('repayment_option', 'none')
            currency_symbol = '€' if currency == 'EUR' else '£'
            payment_schedule = calculator.generate_payment_schedule(result, currency_symbol)
            result['payment_schedule'] = payment_schedule
        except Exception as e:
            app.logger.warning(f"Payment schedule generation failed in fresh calculation: {str(e)}")
            result['payment_schedule'] = []
        
        # Add currency symbol and field mappings
        result['currency'] = currency
        result['currency_symbol'] = '£' if currency == 'GBP' else '€'
        result['currencySymbol'] = result['currency_symbol']  # camelCase for DOCX
        
        # Add all the original form data for completeness
        result.update(form_data)
        
        return result
        
    except Exception as e:
        app.logger.error(f"Fresh calculation error: {str(e)}")
        # Fallback to original data with currency symbol added
        form_data['currency_symbol'] = '£' if form_data.get('currency', 'GBP') == 'GBP' else '€'
        form_data['currencySymbol'] = form_data['currency_symbol']
        return form_data

@app.errorhandler(403)
def forbidden(error):
    return render_template('errors/403.html'), 403

# Template filters
@app.template_filter('currency')
def currency_filter(amount, currency='GBP'):
    return format_currency(amount, currency)

@app.template_filter('percentage')
def percentage_filter(value, decimal_places=2):
    return f"{value:.{decimal_places}f}%"

@app.template_filter('date_format')
def date_format_filter(date, format='%d/%m/%Y'):
    if date:
        return date.strftime(format)
    return ''

# Context processors
@app.context_processor
def inject_user():
    return dict(current_user=current_user)

@app.context_processor
def inject_now():
    return dict(now=datetime.utcnow())

@app.route('/download-professional-quote', methods=['POST'])
@cross_origin()
def download_professional_quote():
    """Generate and download professional DOCX quote matching Aylesbury format"""
    try:
        # Handle both JSON and form data
        if request.is_json:
            calculation_data = request.get_json()
        else:
            # Handle form data
            calculation_data = request.form.to_dict()
            # Parse any JSON strings back to objects
            for key, value in calculation_data.items():
                if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
                    try:
                        calculation_data[key] = json.loads(value)
                    except:
                        pass  # Keep as string if JSON parse fails
        
        if not calculation_data:
            app.logger.error('No calculation data provided in request for professional DOCX generation')
            return jsonify({'error': 'No calculation data provided'}), 400
        
        # Debug: Log what we're actually using for DOCX generation
        app.logger.info(f'Professional DOCX using request data - Loan Type: {calculation_data.get("loan_type", "NOT_FOUND")}')
        app.logger.info(f'Professional DOCX using request data - grossAmount: {calculation_data.get("grossAmount", "NOT_FOUND")}')
        app.logger.info(f'Generating professional DOCX with data keys: {list(calculation_data.keys()) if isinstance(calculation_data, dict) else "Not a dict"}')
        
        # Perform fresh calculation to get proper currency symbols and calculated values
        fresh_calculation = perform_fresh_calculation_for_download(calculation_data)
        
        # Generate professional DOCX using the fresh calculation results
        docx_content = generate_professional_quote_docx(fresh_calculation)
        
        if not docx_content:
            app.logger.error('Professional DOCX generation returned empty content')
            return jsonify({'error': 'Professional DOCX generation failed - empty content'}), 500

        # Create response with comprehensive headers
        response = make_response(docx_content)
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        response.headers['Content-Disposition'] = 'attachment; filename="Professional_Loan_Quote.docx"'
        response.headers['Content-Length'] = str(len(docx_content))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        # Add CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        
        app.logger.info(f'Professional DOCX response created successfully, size: {len(docx_content)} bytes')
        
        return response
        
    except Exception as e:
        app.logger.error(f"Professional PDF generation error: {str(e)}")
        return jsonify({'error': 'Professional PDF generation failed'}), 500



@app.route('/download-pdf-quote', methods=['POST'])
@cross_origin()
def download_pdf_quote():
    """Generate and download PDF quote with charts"""
    try:
        # Get calculation data directly from the request - NO CACHING
        calculation_data = request.get_json()
        
        if not calculation_data:
            app.logger.error('No calculation data provided in request for PDF generation')
            return jsonify({'error': 'No calculation data provided'}), 400
        
        app.logger.info(f'PDF generation - calculation_data keys: {list(calculation_data.keys()) if calculation_data else "None"}')
        if calculation_data:
            app.logger.info(f'PDF generation - grossAmount: {calculation_data.get("grossAmount")}, interestRate: {calculation_data.get("interestRate")}')
        
        # Convert calculation data to quote format with correct field names for PDF generator
        quote_data = {
            'id': datetime.now().strftime('%Y%m%d%H%M%S'),
            'grossAmount': calculation_data.get('grossAmount', calculation_data.get('gross_amount', 0)),
            'netAdvance': calculation_data.get('netAdvance', calculation_data.get('net_advance', 0)),
            'interestRate': calculation_data.get('interestRate', calculation_data.get('annual_rate', 0)),
            'loanTerm': calculation_data.get('loanTerm', calculation_data.get('loan_term', 0)),
            'monthlyPayment': calculation_data.get('monthlyPayment', calculation_data.get('monthly_payment', 0)),
            'totalInterest': calculation_data.get('totalInterest', calculation_data.get('total_interest', 0)),
            'ltv': calculation_data.get('ltv', 0),
            'arrangementFee': calculation_data.get('arrangementFee', calculation_data.get('arrangement_fee', 0)),
            'legalFees': calculation_data.get('legalFees', calculation_data.get('legal_fees', 0)),
            'siteVisitFee': calculation_data.get('siteVisitFee', calculation_data.get('site_visit_fee', 0)),
            'titleInsurance': calculation_data.get('titleInsurance', calculation_data.get('title_insurance', 0)),
            'propertyValue': calculation_data.get('propertyValue', calculation_data.get('property_value', 0)),
            'payment_schedule': calculation_data.get('payment_schedule', []),
            'currency': calculation_data.get('currency', 'GBP'),
            'currency_symbol': calculation_data.get('currency_symbol', '£'),
            'loan_type': calculation_data.get('loan_type', 'bridge'),
            'repayment_option': calculation_data.get('repayment_option', calculation_data.get('repaymentOption', 'none'))
        }
        
        # Application data for PDF
        application_data = {
            'borrower_name': 'Sample Borrower',
            'loan_type': calculation_data.get('loan_type', 'bridge'),
            'property_address': 'Sample Property Address'
        }
        
        # Generate PDF with charts
        pdf_content = generate_quote_pdf(quote_data, application_data)
        
        if not pdf_content:
            app.logger.error('PDF generation returned empty content')
            return jsonify({'error': 'PDF generation failed - empty content'}), 500
        
        # Create response with proper headers
        response = make_response(pdf_content)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Length'] = str(len(pdf_content))
        response.headers['Content-Disposition'] = f'attachment; filename=novellus_quote_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        # Add CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        
        app.logger.info(f'PDF response created successfully, size: {len(pdf_content)} bytes')
        return response
        
    except Exception as e:
        app.logger.error(f'PDF generation error: {str(e)}')
        import traceback
        app.logger.error(f'PDF generation traceback: {traceback.format_exc()}')
        return jsonify({'error': f'Error generating PDF: {str(e)}'}), 500

# BIRT Integration Routes removed to avoid conflicts - using the ones defined later in the file

@app.route('/download-excel-quote', methods=['POST'])
@cross_origin()
def download_excel_quote():
    """Generate and download Excel quote with charts"""
    try:
        # Get calculation data directly from the request - NO CACHING
        calculation_data = request.get_json()
        
        if not calculation_data:
            app.logger.error('No calculation data provided in request for Excel generation')
            return jsonify({'error': 'No calculation data provided'}), 400
        
        app.logger.info(f'Excel generation - calculation_data keys: {list(calculation_data.keys()) if calculation_data else "None"}')
        
        # Perform fresh calculation to get proper currency symbols and calculated values
        fresh_calculation = perform_fresh_calculation_for_download(calculation_data)
        
        # Generate Excel with charts using fresh calculation results
        excel_generator = NovellussExcelGenerator()
        excel_content = excel_generator.generate_quote_excel(fresh_calculation)
        
        if not excel_content:
            app.logger.error('Excel generation returned empty content')
            return jsonify({'error': 'Excel generation failed - empty content'}), 500
        
        # Create response with proper headers
        response = make_response(excel_content)
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Length'] = str(len(excel_content))
        response.headers['Content-Disposition'] = f'attachment; filename=novellus_quote_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        # Add CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        
        app.logger.info(f'Excel response created successfully, size: {len(excel_content)} bytes')
        return response
        
    except Exception as e:
        app.logger.error(f'Excel generation error: {str(e)}')
        import traceback
        app.logger.error(f'Excel generation traceback: {traceback.format_exc()}')
        return jsonify({'error': f'Excel generation failed: {str(e)}'}), 500


@app.route('/save-loan', methods=['POST'])
@cross_origin()
def save_loan():
    """Save loan calculation to database"""
    try:
        # Get calculation data from request
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        loan_name = data.get('loanName', '').strip()
        if not loan_name:
            return jsonify({'error': 'Loan name is required'}), 400
        
        # Check if loan name already exists
        existing_loan = LoanSummary.query.filter_by(loan_name=loan_name).first()
        if existing_loan:
            return jsonify({
                'error': 'A loan with this name already exists. Please choose a different name.',
                'duplicate': True
            }), 409  # Conflict status code
        
        # Perform fresh calculation
        fresh_calculation = perform_fresh_calculation_for_download(data)
        
        if not fresh_calculation:
            return jsonify({'error': 'Failed to calculate loan data'}), 500
        
        # Get loan type from either camelCase (loanType) or snake_case (loan_type)
        loan_type = data.get('loanType') or data.get('loan_type', 'bridge')
        
        # Log the loan type for debugging
        app.logger.info(f"Saving loan with type: {loan_type} (from data keys: {list(data.keys())})")
        
        # Create loan summary record
        loan_summary = LoanSummary(
            loan_name=loan_name,
            version=1,
            loan_type=loan_type,
            currency=data.get('currency', 'GBP'),
            amount_input_type=data.get('amountInputType', 'gross'),
            gross_amount=fresh_calculation.get('grossAmount', 0),
            net_amount=fresh_calculation.get('netAmount', 0),
            property_value=fresh_calculation.get('propertyValue', 0),
            interest_rate=data.get('interestRate', 0),
            loan_term=data.get('loanTerm', 12),
            loan_term_days=fresh_calculation.get('loanTermDays', 365),
            start_date=datetime.strptime(data.get('startDate', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date() if data.get('startDate') else datetime.now().date(),
            end_date=datetime.strptime(data.get('endDate', (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')), '%Y-%m-%d').date() if data.get('endDate') else (datetime.now() + timedelta(days=365)).date(),
            repayment_option=data.get('repaymentOption', 'none'),
            payment_timing=data.get('paymentTiming', 'in_arrears'),
            payment_frequency=data.get('paymentFrequency', 'monthly'),
            capital_repayment=data.get('capitalRepayment', 0),
            flexible_payment=data.get('flexiblePayment', 0),
            arrangement_fee=fresh_calculation.get('arrangementFee', 0),
            arrangement_fee_percentage=data.get('arrangementFeePercentage', 2.0),
            legal_costs=data.get('legalCosts', 1500),
            site_visit_fee=data.get('siteVisitFee', 500),
            title_insurance=fresh_calculation.get('titleInsurance', 1000),
            total_interest=fresh_calculation.get('totalInterest', 0),
            net_advance=fresh_calculation.get('netAdvance', 0),
            total_net_advance=fresh_calculation.get('totalNetAdvance', 0),
            monthly_payment=fresh_calculation.get('monthlyPayment', 0),
            quarterly_payment=fresh_calculation.get('quarterlyPayment', 0),
            start_ltv=fresh_calculation.get('startLtv', 0),
            end_ltv=fresh_calculation.get('endLtv', 0),
            interest_only_total=fresh_calculation.get('interestOnlyTotal', 0),
            interest_savings=fresh_calculation.get('interestSavings', 0),
            savings_percentage=fresh_calculation.get('savingsPercentage', 0),
            day_1_advance=fresh_calculation.get('day1Advance', 0),
            user_input_day_1_advance=data.get('userInputDay1Advance', 0),
            tranches_data=json.dumps(data.get('tranches', []))
        )
        
        db.session.add(loan_summary)
        db.session.flush()  # Get the ID
        
        # Save payment schedule if available
        if 'detailed_payment_schedule' in fresh_calculation and fresh_calculation['detailed_payment_schedule']:
            for i, payment in enumerate(fresh_calculation['detailed_payment_schedule']):
                try:
                    payment_record = PaymentSchedule(
                        loan_summary_id=loan_summary.id,
                        period_number=i + 1,
                        payment_date=parse_payment_date_flexible(payment.get('payment_date', datetime.now().strftime('%Y-%m-%d'))),
                        opening_balance=float(str(payment.get('opening_balance', '0')).replace('£', '').replace(',', '')) if payment.get('opening_balance') else 0,
                        closing_balance=float(str(payment.get('closing_balance', '0')).replace('£', '').replace(',', '')) if payment.get('closing_balance') else 0,
                        balance_change=payment.get('balance_change', ''),
                        total_payment=float(str(payment.get('total_payment', '0')).replace('£', '').replace(',', '')) if payment.get('total_payment') else 0,
                        interest_amount=float(str(payment.get('interest_amount', '0')).replace('£', '').replace(',', '')) if payment.get('interest_amount') else 0,
                        principal_payment=float(str(payment.get('principal_payment', '0')).replace('£', '').replace(',', '')) if payment.get('principal_payment') else 0,
                        tranche_release=float(str(payment.get('tranche_release', '0')).replace('£', '').replace(',', '')) if payment.get('tranche_release') else 0,
                        interest_calculation=payment.get('interest_calculation', '')
                    )
                    db.session.add(payment_record)
                except Exception as pe:
                    app.logger.warning(f"Error saving payment {i+1}: {pe}")
                    continue
        
        db.session.commit()
        
        app.logger.info(f"Loan saved successfully: {loan_name}")
        
        # Trigger Power BI refresh after successful save
        trigger_powerbi_on_save()
        
        return jsonify({
            'success': True,
            'message': f'Loan saved successfully as "{loan_name}"',
            'loan_id': loan_summary.id,
            'loan_name': loan_name
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Save loan error: {str(e)}")
        return jsonify({'error': f'Failed to save loan: {str(e)}'}), 500


@app.route('/loan-history')
def loan_history():
    """Show saved loan history page"""
    try:
        # Get all loan summaries
        loans = LoanSummary.query.order_by(LoanSummary.created_at.desc()).all()
        
        # Get payment schedules for each loan
        loan_data = []
        for loan in loans:
            payment_schedule = PaymentSchedule.query.filter_by(loan_summary_id=loan.id).order_by(PaymentSchedule.period_number).all()
            loan_data.append({
                'loan': loan,
                'payment_schedule': payment_schedule
            })
        
        return render_template('loan_history.html', loan_data=loan_data)
        
    except Exception as e:
        app.logger.error(f"Error loading loan history: {str(e)}")
        return render_template('loan_history.html', loan_data=[])

@app.route('/user-manual')
def user_manual():
    """Display the User Manual page"""
    try:
        # Read the USER_MANUAL.md file
        with open('USER_MANUAL.md', 'r', encoding='utf-8') as f:
            manual_content = f.read()
        
        return render_template('user_manual.html', manual_content=manual_content)
    except FileNotFoundError:
        flash('User Manual not found', 'error')
        return redirect(url_for('calculator_page'))
    except Exception as e:
        app.logger.error(f"Error loading user manual: {str(e)}")
        flash('Error loading user manual', 'error')
        return redirect(url_for('calculator_page'))


@app.route('/api/saved-loans', methods=['GET'])
@cross_origin()
def get_saved_loans():
    """Get all saved loans"""
    try:
        # Get filter parameters
        search = request.args.get('search', '').strip()
        loan_type_filter = request.args.get('loan_type', '').strip()
        
        # Build query
        query = LoanSummary.query
        
        if search:
            query = query.filter(LoanSummary.loan_name.ilike(f'%{search}%'))
        
        if loan_type_filter:
            query = query.filter(LoanSummary.loan_type == loan_type_filter)
        
        # Order by creation date, newest first
        loans = query.order_by(LoanSummary.created_at.desc()).all()
        
        # Convert to JSON with comprehensive edit data
        loans_data = []
        for loan in loans:
            loan_data = {
                'id': loan.id,
                'loan_name': loan.loan_name,
                'version': loan.version,
                'created_at': loan.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'loan_type': loan.loan_type,
                'currency': loan.currency,
                'gross_amount': float(loan.gross_amount) if loan.gross_amount else 0,
                'total_interest': float(loan.total_interest) if loan.total_interest else 0,
                'loan_term': loan.loan_term,
                'interest_rate': float(loan.interest_rate) if loan.interest_rate else 0,
                'repayment_option': loan.repayment_option,
                
                # Additional data needed for editing
                'amountInputType': loan.amount_input_type if loan.amount_input_type else 'gross',
                'netAmount': float(loan.net_amount) if loan.net_amount else 0,
                'propertyValue': float(loan.property_value) if loan.property_value else 0,
                'startDate': loan.start_date.strftime('%Y-%m-%d') if loan.start_date else '',
                'endDate': loan.end_date.strftime('%Y-%m-%d') if loan.end_date else '',
                'legalFees': float(loan.legal_costs) if loan.legal_costs else 1500,
                'siteVisitFee': float(loan.site_visit_fee) if loan.site_visit_fee else 500,
                'arrangementFeePercentage': float(loan.arrangement_fee_percentage) if loan.arrangement_fee_percentage else 2.0,
                'titleInsuranceRate': 0.01,  # Fixed rate
                'paymentTiming': loan.payment_timing if loan.payment_timing else 'advance',
                'paymentFrequency': loan.payment_frequency if loan.payment_frequency else 'monthly',
                'capitalRepayment': float(loan.capital_repayment) if loan.capital_repayment else 0,
                'flexiblePayment': float(loan.flexible_payment) if loan.flexible_payment else 0,
                'day1Advance': float(loan.day_1_advance) if loan.day_1_advance else 0,
                'trancheMode': 'manual',  # Default value
                'tranches': []
            }
            
            # Extract tranches data for development loans
            try:
                if hasattr(loan, 'tranches_data') and loan.tranches_data:
                    if isinstance(loan.tranches_data, str):
                        import json
                        loan_data['tranches'] = json.loads(loan.tranches_data)
                    else:
                        loan_data['tranches'] = loan.tranches_data
            except Exception as e:
                app.logger.warning(f"Could not parse tranches for loan {loan.id}: {e}")
                loan_data['tranches'] = []
                
            loans_data.append(loan_data)
        
        return jsonify({
            'success': True,
            'loans': loans_data,
            'total_count': len(loans_data)
        })
        
    except Exception as e:
        app.logger.error(f"Get saved loans error: {str(e)}")
        return jsonify({'error': f'Failed to retrieve loans: {str(e)}'}), 500


@app.route('/api/loan/<int:loan_id>', methods=['GET'])
@cross_origin()
def get_loan_details(loan_id):
    """Get detailed loan information by ID"""
    try:
        loan = LoanSummary.query.get_or_404(loan_id)
        
        # Get payment schedule
        payment_schedule = PaymentSchedule.query.filter_by(loan_summary_id=loan_id).order_by(PaymentSchedule.period_number).all()
        
        # Convert payment schedule to list
        schedule_data = []
        for payment in payment_schedule:
            schedule_data.append({
                'period_number': payment.period_number,
                'payment_date': payment.payment_date.strftime('%d/%m/%Y') if payment.payment_date else '',
                'opening_balance': f"£{payment.opening_balance:,.2f}" if payment.opening_balance else '£0.00',
                'closing_balance': f"£{payment.closing_balance:,.2f}" if payment.closing_balance else '£0.00',
                'balance_change': payment.balance_change or '',
                'total_payment': f"£{payment.total_payment:,.2f}" if payment.total_payment else '£0.00',
                'interest_amount': f"£{payment.interest_amount:,.2f}" if payment.interest_amount else '£0.00',
                'principal_payment': f"£{payment.principal_payment:,.2f}" if payment.principal_payment else '£0.00',
                'tranche_release': f"£{payment.tranche_release:,.2f}" if payment.tranche_release else '£0.00',
                'interest_calculation': payment.interest_calculation or ''
            })
        
        # Convert loan data to JSON with comprehensive edit parameters
        loan_data = {
            'id': loan.id,
            'loan_name': loan.loan_name,
            'version': loan.version,
            'created_at': loan.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            
            # Core loan parameters for editing
            'loan_type': loan.loan_type,
            'currency': loan.currency,
            'amount_input_type': getattr(loan, 'amount_input_type', 'gross'),
            'gross_amount': float(loan.gross_amount) if loan.gross_amount else 0,
            'net_amount': float(getattr(loan, 'net_amount', 0)) if getattr(loan, 'net_amount', None) else 0,
            'property_value': float(loan.property_value) if loan.property_value else 0,
            'interest_rate': float(loan.interest_rate) if loan.interest_rate else 0,
            'loan_term': loan.loan_term,
            'start_date': loan.start_date.strftime('%Y-%m-%d') if loan.start_date else '',
            'end_date': loan.end_date.strftime('%Y-%m-%d') if loan.end_date else '',
            
            # Repayment and fee parameters
            'repayment_option': loan.repayment_option,
            'arrangement_fee': float(loan.arrangement_fee) if loan.arrangement_fee else 0,
            'arrangement_fee_percentage': float(loan.arrangement_fee_percentage) if loan.arrangement_fee_percentage else 2.0,
            'legal_fees': float(loan.legal_costs) if loan.legal_costs else 1500,
            'site_visit_fee': float(loan.site_visit_fee) if loan.site_visit_fee else 500,
            'title_insurance_rate': 0.01,  # Fixed rate
            
            # Payment parameters
            'payment_timing': loan.payment_timing if loan.payment_timing else 'advance',
            'payment_frequency': loan.payment_frequency if loan.payment_frequency else 'monthly',
            'capital_repayment': float(loan.capital_repayment) if loan.capital_repayment else 0,
            'flexible_payment': float(loan.flexible_payment) if loan.flexible_payment else 0,
            
            # Day 1 advance for development loans
            'day1_advance': float(loan.day_1_advance) if loan.day_1_advance else 0,
            
            # Tranche information for development loans
            'tranche_mode': 'manual',  # Default value
            'tranches': [],  # Will be populated from loan metadata if available
            
            # Calculated results for display (camelCase for JavaScript compatibility)
            'grossAmount': float(loan.gross_amount) if loan.gross_amount else 0,
            'netAmount': float(loan.net_amount) if loan.net_amount else 0,
            'totalInterest': float(loan.total_interest) if loan.total_interest else 0,
            'arrangementFee': float(loan.arrangement_fee) if loan.arrangement_fee else 0,
            'netAdvance': float(loan.net_advance) if loan.net_advance else 0,
            'totalNetAdvance': float(loan.total_net_advance) if loan.total_net_advance else 0,
            'monthlyPayment': float(loan.monthly_payment) if loan.monthly_payment else 0,
            'propertyValue': float(loan.property_value) if loan.property_value else 0,
            'legalFees': float(loan.legal_costs) if loan.legal_costs else 1500,
            'siteVisitFee': float(loan.site_visit_fee) if loan.site_visit_fee else 500,
            'titleInsurance': float(loan.title_insurance) if loan.title_insurance else 0,
            'ltvRatio': float(loan.start_ltv) if loan.start_ltv else 0,
            'startLtv': float(loan.start_ltv) if loan.start_ltv else 0,
            'endLtv': float(loan.end_ltv) if loan.end_ltv else 0,
            
            # Date fields formatted for JavaScript
            'startDate': loan.start_date.strftime('%Y-%m-%d') if loan.start_date else '',
            'endDate': loan.end_date.strftime('%Y-%m-%d') if loan.end_date else '',
            'loanTerm': loan.loan_term if loan.loan_term else 0,
            'loanTermDays': loan.loan_term_days if loan.loan_term_days else 0,
            
            # User interface fields (camelCase)
            'amountInputType': loan.amount_input_type if loan.amount_input_type else 'gross',
            'interestRate': float(loan.interest_rate) if loan.interest_rate else 0,
            'repaymentOption': loan.repayment_option,
            'paymentTiming': loan.payment_timing if loan.payment_timing else 'advance',
            'paymentFrequency': loan.payment_frequency if loan.payment_frequency else 'monthly',
            'capitalRepayment': float(loan.capital_repayment) if loan.capital_repayment else 0,
            'flexiblePayment': float(loan.flexible_payment) if loan.flexible_payment else 0,
            'arrangementFeePercentage': float(loan.arrangement_fee_percentage) if loan.arrangement_fee_percentage else 2.0,
            'titleInsuranceRate': 0.01,  # Fixed rate
            
            # Development loan specific fields
            'day1Advance': float(loan.day_1_advance) if loan.day_1_advance else 0,
            'userInputDay1Advance': float(loan.user_input_day_1_advance) if loan.user_input_day_1_advance else 0,
            
            # Payment schedule
            'detailed_payment_schedule': schedule_data
        }
        
        # Try to extract tranche information from stored tranches_data 
        try:
            if hasattr(loan, 'tranches_data') and loan.tranches_data:
                if isinstance(loan.tranches_data, str):
                    import json
                    loan_data['tranches'] = json.loads(loan.tranches_data)
                else:
                    loan_data['tranches'] = loan.tranches_data
            else:
                loan_data['tranches'] = []
        except Exception as e:
            app.logger.warning(f"Could not parse loan tranches_data: {e}")
            loan_data['tranches'] = []
        
        return jsonify({
            'success': True,
            'loan': loan_data
        })
        
    except Exception as e:
        app.logger.error(f"Get loan details error: {str(e)}")
        return jsonify({'error': f'Failed to retrieve loan details: {str(e)}'}), 500


@app.route('/api/loan/<int:loan_id>', methods=['DELETE'])
@cross_origin()
def delete_loan(loan_id):
    """Delete a saved loan calculation"""
    try:
        loan = LoanSummary.query.get_or_404(loan_id)
        loan_name = loan.loan_name
        
        # Delete the loan (cascade will handle payment schedule)
        db.session.delete(loan)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Loan "{loan_name}" has been deleted successfully'
        })
        
    except Exception as e:
        app.logger.error(f"Delete loan error: {str(e)}")
        return jsonify({'error': f'Failed to delete loan: {str(e)}'}), 500


@app.route('/generate-saved-quote/<int:loan_id>', methods=['POST'])
@cross_origin()
def generate_saved_quote(loan_id):
    """Generate quote from saved loan data"""
    try:
        loan = LoanSummary.query.get_or_404(loan_id)
        quote_type = request.json.get('quote_type', 'professional') if request.is_json else request.form.get('quote_type', 'professional')
        
        # Convert loan data back to calculation format
        calculation_data = {
            'loanType': loan.loan_type,
            'currency': loan.currency,
            'grossAmount': float(loan.gross_amount) if loan.gross_amount else 0,
            'totalInterest': float(loan.total_interest) if loan.total_interest else 0,
            'arrangementFee': float(loan.arrangement_fee) if loan.arrangement_fee else 0,
            'netAdvance': float(loan.net_advance) if loan.net_advance else 0,
            'totalNetAdvance': float(loan.total_net_advance) if loan.total_net_advance else 0,
            'propertyValue': float(loan.property_value) if loan.property_value else 0,
            'currencySymbol': '£' if loan.currency == 'GBP' else '€',
            'legalCosts': float(loan.legal_costs) if loan.legal_costs else 1500,
            'siteVisitFee': float(loan.site_visit_fee) if loan.site_visit_fee else 500,
            'titleInsurance': float(loan.title_insurance) if loan.title_insurance else 1000
        }
        
        # Add payment schedule
        payment_schedule = PaymentSchedule.query.filter_by(loan_summary_id=loan_id).order_by(PaymentSchedule.period_number).all()
        schedule_data = []
        for payment in payment_schedule:
            schedule_data.append({
                'payment_date': payment.payment_date.strftime('%d/%m/%Y') if payment.payment_date else '',
                'opening_balance': f"£{payment.opening_balance:,.2f}" if payment.opening_balance else '£0.00',
                'closing_balance': f"£{payment.closing_balance:,.2f}" if payment.closing_balance else '£0.00',
                'balance_change': payment.balance_change or '',
                'total_payment': f"£{payment.total_payment:,.2f}" if payment.total_payment else '£0.00',
                'interest_amount': f"£{payment.interest_amount:,.2f}" if payment.interest_amount else '£0.00',
                'principal_payment': f"£{payment.principal_payment:,.2f}" if payment.principal_payment else '£0.00',
                'tranche_release': f"£{payment.tranche_release:,.2f}" if payment.tranche_release else '£0.00',
                'interest_calculation': payment.interest_calculation or ''
            })
        calculation_data['detailed_payment_schedule'] = schedule_data
        
        # Generate quote based on type
        if quote_type == 'professional':
            docx_content = generate_professional_quote_docx(calculation_data)
            if not docx_content:
                return jsonify({'error': 'Professional quote generation failed'}), 500
            
            response = make_response(docx_content)
            response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            response.headers['Content-Disposition'] = f'attachment; filename="{loan.loan_name}_Professional_Quote.docx"'
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            response.headers['Content-Length'] = str(len(docx_content))
            response.headers['Cache-Control'] = 'no-cache'
            return response
            
        elif quote_type == 'excel':
            excel_generator = NovellussExcelGenerator()
            excel_content = excel_generator.generate_quote_excel(calculation_data)
            
            if not excel_content:
                return jsonify({'error': 'Excel generation failed'}), 500
            
            response = make_response(excel_content)
            response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response.headers['Content-Disposition'] = f'attachment; filename="{loan.loan_name}_Quote.xlsx"'
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            response.headers['Content-Length'] = str(len(excel_content))
            response.headers['Cache-Control'] = 'no-cache'
            return response
        
        else:
            return jsonify({'error': 'Invalid quote type'}), 400
            
    except Exception as e:
        app.logger.error(f"Generate saved quote error: {str(e)}")
        return jsonify({'error': f'Failed to generate quote: {str(e)}'}), 500




@app.route('/database-info')
def database_info():
    """Show comprehensive database information including loan calculator data"""
    try:
        # Get database connection info
        db_url = os.environ.get('DATABASE_URL', 'Not configured')
        pghost = os.environ.get('PGHOST', 'Not available')
        pgport = os.environ.get('PGPORT', 'Not available')
        pgdatabase = os.environ.get('PGDATABASE', 'Not available')
        pguser = os.environ.get('PGUSER', 'Not available')
        pgpassword_status = 'Configured' if os.environ.get('PGPASSWORD') else 'Not configured'
        
        connection_info = {
            'Database URL': db_url,
            'Host': pghost,
            'Port': pgport,
            'Database': pgdatabase,
            'User': pguser,
            'Password': pgpassword_status
        }
        
        # Get loan calculator storage statistics
        from models import LoanSummary, PaymentSchedule, User
        
        loan_count = LoanSummary.query.count()
        schedule_count = PaymentSchedule.query.count()
        user_count = User.query.count()
        
        # Get recent loan activity
        recent_loans = LoanSummary.query.order_by(LoanSummary.created_at.desc()).limit(5).all()
        
        storage_stats = {
            'Total Loans': loan_count,
            'Payment Schedule Entries': schedule_count,
            'Registered Users': user_count,
            'Database Status': 'Operational' if loan_count > 0 else 'Empty'
        }
        
        return render_template('database_info.html', 
                             connection_info=connection_info,
                             storage_stats=storage_stats,
                             recent_loans=recent_loans)
        
    except Exception as e:
        app.logger.error(f"Database info error: {str(e)}")
        flash(f'Error retrieving database information: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/database-info')
def get_database_info():
    """Get database connection information for display"""
    try:
        # Get database URL from environment
        database_url = os.environ.get('DATABASE_URL', 'Not configured')
        
        # Parse database information
        if database_url.startswith('postgresql://'):
            # Parse PostgreSQL connection string
            # Format: postgresql://user:password@host:port/database
            url_parts = database_url.replace('postgresql://', '').split('@')
            if len(url_parts) == 2:
                user_pass = url_parts[0].split(':')
                host_port_db = url_parts[1].split('/')
                host_port = host_port_db[0].split(':')
                
                db_info = {
                    'type': 'PostgreSQL',
                    'host': host_port[0] if len(host_port) > 0 else 'localhost',
                    'port': host_port[1] if len(host_port) > 1 else '5432',
                    'database': host_port_db[1] if len(host_port_db) > 1 else 'novellus_loans',
                    'username': user_pass[0] if len(user_pass) > 0 else 'novellus_user',
                    'password': '***masked***',  # Never show real password
                    'connection_string': database_url.replace(user_pass[1], '***masked***') if len(user_pass) > 1 else database_url,
                    'status': 'Connected'
                }
            else:
                db_info = {
                    'type': 'PostgreSQL',
                    'connection_string': database_url,
                    'status': 'Connected'
                }
        elif database_url.startswith('sqlite:///'):
            db_info = {
                'type': 'SQLite',
                'database_file': database_url.replace('sqlite:///', ''),
                'connection_string': database_url,
                'status': 'Connected'
            }
        else:
            db_info = {
                'type': 'Unknown',
                'connection_string': database_url,
                'status': 'Unknown'
            }
        
        # Test database connection
        try:
            with db.engine.connect() as conn:
                result = conn.execute(sa.text("SELECT 1"))
                result.fetchone()
            db_info['status'] = 'Connected'
            db_info['last_tested'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            db_info['status'] = f'Connection Error: {str(e)}'
            db_info['last_tested'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Get table information
        try:
            inspector = sa.inspect(db.engine)
            tables = inspector.get_table_names()
            db_info['tables'] = tables
            db_info['table_count'] = len(tables)
            
            # Get record counts for key tables
            table_counts = {}
            for table in ['loan_summary', 'payment_schedule', 'users', 'applications']:
                if table in tables:
                    try:
                        with db.engine.connect() as conn:
                            result = conn.execute(sa.text(f"SELECT COUNT(*) FROM {table}"))
                            count = result.fetchone()[0]
                            table_counts[table] = count
                    except:
                        table_counts[table] = 'Error'
            db_info['record_counts'] = table_counts
            
        except Exception as e:
            db_info['table_error'] = str(e)
        
        return jsonify(db_info)
        
    except Exception as e:
        return jsonify({
            'type': 'Error',
            'status': f'Error retrieving database info: {str(e)}',
            'last_tested': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 500


# BIRT Report Integration Routes - REMOVED for simplified on-premise deployment

# Working Report Generator Routes (Alternative to BIRT)
@app.route('/generate-working-report/<report_type>/<int:loan_id>')
def generate_working_report(report_type, loan_id):
    """Generate reports using the working report generator"""
    if not working_report_generator:
        return jsonify({'error': 'Working report generator not available'}), 503
    
    try:
        if report_type == 'pdf':
            result = working_report_generator.generate_loan_summary_pdf(loan_id)
        elif report_type == 'excel':
            result = working_report_generator.generate_loan_summary_excel(loan_id)
        else:
            return jsonify({'error': 'Invalid report type'}), 400
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'filename': result['filename'],
                'download_url': f'/download-working-report/{result["filename"]}'
            })
        else:
            return jsonify({'error': result['error']}), 500
            
    except Exception as e:
        app.logger.error(f"Error generating working report: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download-working-report/<filename>')
def download_working_report(filename):
    """Download generated report file"""
    try:
        report_dir = os.path.join(os.getcwd(), 'reports_output')
        filepath = os.path.join(report_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Report file not found'}), 404
        
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        app.logger.error(f"Error downloading report: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/powerbi-config')
def powerbi_config():
    return render_template('powerbi_config.html')

@app.route('/powerbi-scheduler')
@login_required
def powerbi_scheduler():
    """Power BI Refresh Scheduler Interface"""
    return render_template('powerbi_scheduler.html')

# Power BI Configuration API endpoints
@app.route('/api/powerbi/reports', methods=['GET'])
def get_powerbi_reports():
    """Get all configured Power BI reports"""
    try:
        # Default reports configuration
        reports = {
            'main': {
                'name': 'Loan Summary Report',
                'baseUrl': 'https://app.powerbi.com/groups/71153f62-9f44-47cd-b6d5-c3e56e8977ba/rdlreports/3bcd8dd2-4773-4372-9a19-1174c108aee5?ctid=16f1922b-4a40-4f3f-8c40-afbd1d4a0e21',
                'icon': 'fas fa-chart-bar'
            }
        }
        
        # Try to load from file if exists
        import os
        config_file = 'powerbi_reports.json'
        if os.path.exists(config_file):
            try:
                import json
                with open(config_file, 'r') as f:
                    file_reports = json.load(f)
                    reports.update(file_reports)
            except Exception as e:
                import logging
                logging.error(f"Error loading Power BI config: {e}")
        
        return jsonify({'success': True, 'reports': reports})
    except Exception as e:
        import logging
        logging.error(f"Error getting Power BI reports: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/powerbi/reports', methods=['POST'])
def add_powerbi_report():
    """Add a new Power BI report"""
    try:
        data = request.get_json()
        
        required_fields = ['key', 'name', 'baseUrl']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Load existing reports
        import os
        import json
        config_file = 'powerbi_reports.json'
        reports = {}
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    reports = json.load(f)
            except:
                reports = {}
        
        # Add new report with dynamic parameters
        reports[data['key']] = {
            'name': data['name'],
            'baseUrl': data['baseUrl'],
            'icon': data.get('icon', 'fas fa-chart-bar'),
            'parameters': data.get('parameters', [])
        }
        
        # Save to file
        with open(config_file, 'w') as f:
            json.dump(reports, f, indent=2)
        
        return jsonify({'success': True, 'message': 'Report added successfully'})
    except Exception as e:
        import logging
        logging.error(f"Error adding Power BI report: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/powerbi/reports/<report_key>', methods=['PUT'])
def update_powerbi_report(report_key):
    """Update an existing Power BI report"""
    try:
        data = request.get_json()
        
        # Load existing reports
        import os
        import json
        config_file = 'powerbi_reports.json'
        reports = {}
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    reports = json.load(f)
            except:
                reports = {}
        
        if report_key not in reports and report_key != 'main':
            return jsonify({'success': False, 'error': 'Report not found'}), 404
        
        # Update report
        reports[report_key] = {
            'name': data.get('name', reports.get(report_key, {}).get('name', '')),
            'baseUrl': data.get('baseUrl', reports.get(report_key, {}).get('baseUrl', '')),
            'icon': data.get('icon', reports.get(report_key, {}).get('icon', 'fas fa-chart-bar')),
            'parameters': data.get('parameters', reports.get(report_key, {}).get('parameters', []))
        }
        
        # Save to file
        with open(config_file, 'w') as f:
            json.dump(reports, f, indent=2)
        
        return jsonify({'success': True, 'message': 'Report updated successfully'})
    except Exception as e:
        import logging
        logging.error(f"Error updating Power BI report: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/powerbi/reports/<report_key>', methods=['DELETE'])
def delete_powerbi_report(report_key):
    """Delete a Power BI report"""
    try:
        if report_key == 'main':
            return jsonify({'success': False, 'error': 'Cannot delete the main report'}), 400
        
        # Load existing reports
        import os
        import json
        config_file = 'powerbi_reports.json'
        reports = {}
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    reports = json.load(f)
            except:
                reports = {}
        
        if report_key not in reports:
            return jsonify({'success': False, 'error': 'Report not found'}), 404
        
        # Delete report
        del reports[report_key]
        
        # Save to file
        with open(config_file, 'w') as f:
            json.dump(reports, f, indent=2)
        
        return jsonify({'success': True, 'message': 'Report deleted successfully'})
    except Exception as e:
        import logging
        logging.error(f"Error deleting Power BI report: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Global scheduler instance for Power BI
_global_scheduler = None

@app.route('/api/powerbi/test-refresh', methods=['POST'])
@cross_origin()
def test_powerbi_refresh():
    """Test immediate Power BI refresh using final working code"""
    if not POWERBI_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Power BI refresh not available - selenium not installed'
        }), 503
    
    try:
        data = request.get_json() or {}
        username = data.get('username')
        password = data.get('password')
        dataset_url = data.get('dataset_url')
        
        if not all([username, password, dataset_url]):
            return jsonify({
                'success': False,
                'error': 'Missing Power BI credentials or dataset URL'
            }), 400
        
        # Use final working refresher
        refresher = FinalWorkingPowerBIRefresher(username, password, dataset_url)
        
        if hasattr(app, 'powerbi_notifications'):
            refresher.add_notification_callback(app.powerbi_notifications.add_notification)
        
        # Run refresh using final working method
        success = refresher.refresh_dataset_final()
        
        return jsonify({
            'success': success,
            'message': 'Test refresh completed successfully' if success else 'Test refresh failed'
        })
        
    except Exception as e:
        app.logger.error(f"Test refresh error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/powerbi/start-schedule', methods=['POST'])
@cross_origin()
def start_powerbi_schedule():
    """Start scheduled Power BI refresh"""
    global scheduler_active
    
    if not POWERBI_AVAILABLE or not scheduler:
        return jsonify({
            'success': False,
            'error': 'Power BI scheduling not available'
        }), 503
    
    try:
        data = request.get_json() or {}
        username = data.get('username')
        password = data.get('password')
        dataset_url = data.get('dataset_url')
        interval = int(data.get('interval', 60))  # Default 60 minutes
        
        if not all([username, password, dataset_url]):
            return jsonify({
                'success': False,
                'error': 'Missing Power BI credentials or dataset URL'
            }), 400
        
        # Stop any existing scheduled job
        try:
            scheduler.remove_job('powerbi_refresh')
        except:
            pass
        
        # Create scheduled refresh function
        def scheduled_refresh():
            try:
                app.logger.info("Starting scheduled Power BI refresh...")
                refresher = FinalWorkingPowerBIRefresher(username, password, dataset_url)
                success = refresher.refresh_dataset_final()
                app.logger.info(f"Scheduled Power BI refresh completed: {success}")
            except Exception as e:
                app.logger.error(f"Scheduled Power BI refresh error: {str(e)}")
        
        # Schedule the job
        scheduler.add_job(
            scheduled_refresh,
            trigger=IntervalTrigger(minutes=interval),
            id='powerbi_refresh',
            replace_existing=True
        )
        
        scheduler_active = True
        app.logger.info(f"Power BI refresh scheduled every {interval} minutes")
        
        # Save schedule configuration for persistence
        schedule_config = {
            'enabled': True,
            'username': username,
            'password': password,
            'dataset_url': dataset_url,
            'interval': interval,
            'created_at': datetime.now().isoformat()
        }
        
        try:
            with open('powerbi_schedule_config.json', 'w') as f:
                json.dump(schedule_config, f, indent=2)
            app.logger.info("Power BI schedule configuration saved for persistence")
        except Exception as e:
            app.logger.error(f"Failed to save schedule configuration: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': f'Power BI refresh scheduled every {interval} minutes (persistent)'
        })
        
    except Exception as e:
        app.logger.error(f"Start schedule error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/powerbi/stop-schedule', methods=['POST'])
@cross_origin()
def stop_powerbi_schedule():
    """Stop scheduled Power BI refresh"""
    global scheduler_active
    
    try:
        if scheduler:
            # Remove the scheduled job
            try:
                scheduler.remove_job('powerbi_refresh')
                scheduler_active = False
                app.logger.info("Power BI refresh schedule stopped")
                
                # Update saved configuration to disabled
                try:
                    schedule_config_file = 'powerbi_schedule_config.json'
                    if os.path.exists(schedule_config_file):
                        with open(schedule_config_file, 'r') as f:
                            config = json.load(f)
                        config['enabled'] = False
                        config['stopped_at'] = datetime.now().isoformat()
                        with open(schedule_config_file, 'w') as f:
                            json.dump(config, f, indent=2)
                        app.logger.info("Power BI schedule configuration updated to disabled")
                except Exception as e:
                    app.logger.error(f"Failed to update schedule configuration: {str(e)}")
                
                return jsonify({
                    'success': True,
                    'message': 'Power BI refresh schedule stopped (persistent)'
                })
            except:
                scheduler_active = False
                
                # Still update configuration even if no job was running
                try:
                    schedule_config_file = 'powerbi_schedule_config.json'
                    if os.path.exists(schedule_config_file):
                        with open(schedule_config_file, 'r') as f:
                            config = json.load(f)
                        config['enabled'] = False
                        config['stopped_at'] = datetime.now().isoformat()
                        with open(schedule_config_file, 'w') as f:
                            json.dump(config, f, indent=2)
                except Exception as e:
                    app.logger.error(f"Failed to update schedule configuration: {str(e)}")
                
                return jsonify({
                    'success': True,
                    'message': 'No active schedule to stop'
                })
        else:
            return jsonify({
                'success': False,
                'error': 'Scheduler not available'
            })
        
    except Exception as e:
        app.logger.error(f"Stop schedule error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/powerbi/schedule-status', methods=['GET'])
@cross_origin()
def get_powerbi_schedule_status():
    """Get current Power BI schedule status"""
    global scheduler_active
    
    try:
        if scheduler and scheduler_active:
            try:
                job = scheduler.get_job('powerbi_refresh')
                if job:
                    next_run = job.next_run_time.isoformat() if job.next_run_time else None
                    
                    # Get saved configuration details
                    config_details = {}
                    try:
                        schedule_config_file = 'powerbi_schedule_config.json'
                        if os.path.exists(schedule_config_file):
                            with open(schedule_config_file, 'r') as f:
                                config = json.load(f)
                            config_details = {
                                'interval': config.get('interval', 'Unknown'),
                                'created_at': config.get('created_at', 'Unknown'),
                                'dataset_url': config.get('dataset_url', 'Unknown')[:50] + '...' if len(config.get('dataset_url', '')) > 50 else config.get('dataset_url', 'Unknown'),
                                'has_credentials': bool(config.get('username') and config.get('password')),
                                'username': config.get('username', 'Not saved')[:20] + '...' if len(config.get('username', '')) > 20 else config.get('username', 'Not saved')
                            }
                    except:
                        pass
                    
                    return jsonify({
                        'scheduler_running': True,
                        'next_run': next_run,
                        'total_jobs': 1,
                        'persistent': True,
                        'config': config_details
                    })
                else:
                    scheduler_active = False
                    return jsonify({
                        'scheduler_running': False,
                        'next_run': None,
                        'total_jobs': 0,
                        'persistent': False
                    })
            except:
                scheduler_active = False
                return jsonify({
                    'scheduler_running': False,
                    'next_run': None,
                    'total_jobs': 0,
                    'persistent': False
                })
        else:
            return jsonify({
                'scheduler_running': False,
                'next_run': None,
                'total_jobs': 0,
                'persistent': False
            })
        
    except Exception as e:
        app.logger.error(f"Schedule status error: {str(e)}")
        return jsonify({
            'scheduler_running': False,
            'next_run': None,
            'total_jobs': 0
        }), 500

# Power BI Refresh Routes
@app.route('/api/powerbi/refresh', methods=['POST'])
@cross_origin()
def trigger_powerbi_refresh():
    """Trigger Power BI dataset refresh in background"""
    if not POWERBI_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Power BI refresh not available - selenium not installed'
        }), 503
    
    try:
        # Get Power BI credentials from request or environment
        data = request.get_json() or {}
        username = data.get('username') or os.environ.get('POWERBI_USERNAME')
        password = data.get('password') or os.environ.get('POWERBI_PASSWORD')
        dataset_url = data.get('dataset_url') or os.environ.get('POWERBI_DATASET_URL')
        
        if not all([username, password, dataset_url]):
            return jsonify({
                'success': False,
                'error': 'Missing Power BI credentials or dataset URL'
            }), 400
        
        # Start refresh in background thread
        def run_refresh():
            try:
                from powerbi_refresh import PowerBIRefresher
                from powerbi_working_refresh import WorkingPowerBIRefresher
                from powerbi_enhanced_working_refresh import EnhancedWorkingPowerBIRefresher
                from powerbi_final_working_refresh import FinalWorkingPowerBIRefresher
                # Use the final working refresh code with exact user Edge browser setup
                refresher = FinalWorkingPowerBIRefresher(username, password, dataset_url)
                if hasattr(app, 'powerbi_notifications'):
                    refresher.add_notification_callback(app.powerbi_notifications.add_notification)
                refresher.refresh_dataset_final()
            except Exception as e:
                app.logger.error(f"Power BI refresh failed: {str(e)}")
        
        refresh_thread = threading.Thread(target=run_refresh)
        refresh_thread.daemon = True
        refresh_thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Power BI refresh started in background'
        })
        
    except Exception as e:
        app.logger.error(f"Power BI refresh trigger failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/powerbi/test-connection', methods=['POST'])
@cross_origin()
def test_powerbi_connection():
    """Test Power BI connection without triggering refresh"""
    if not POWERBI_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Power BI connection test not available - selenium not installed'
        }), 503
    
    try:
        # Get Power BI credentials from request
        data = request.get_json() or {}
        username = data.get('username')
        password = data.get('password')
        dataset_url = data.get('dataset_url')
        
        if not all([username, password, dataset_url]):
            return jsonify({
                'success': False,
                'error': 'Missing Power BI credentials or dataset URL'
            }), 400
        
        # Validate URL format
        if 'app.powerbi.com' not in dataset_url:
            return jsonify({
                'success': False,
                'error': 'Invalid Power BI dataset URL format'
            }), 400
        
        # Basic connection test using working refresher
        try:
            from powerbi_working_refresh import WorkingPowerBIRefresher
            refresher = WorkingPowerBIRefresher(username, password, dataset_url)
            
            # Test connection using the working method
            if refresher.test_connection():
                return jsonify({
                    'success': True,
                    'message': 'Connection test passed - credentials and URL appear valid'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to initialize browser for connection test'
                })
                
        except Exception as test_error:
            return jsonify({
                'success': False,
                'error': f'Connection test failed: {str(test_error)}'
            })
        
    except Exception as e:
        app.logger.error(f"Power BI connection test failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/powerbi/notifications')
@cross_origin()
def get_powerbi_notifications():
    """Get Power BI refresh notifications"""
    try:
        since_timestamp = request.args.get('since')
        
        if hasattr(app, 'powerbi_notifications'):
            notifications = app.powerbi_notifications.get_notifications(since_timestamp)
            return jsonify({
                'success': True,
                'notifications': notifications
            })
        else:
            return jsonify({
                'success': True,
                'notifications': []
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/powerbi/pause-schedule', methods=['POST'])
def pause_powerbi_schedule():
    """Pause the current Power BI refresh schedule"""
    global scheduler_active
    
    try:
        if scheduler and scheduler_active:
            try:
                job = scheduler.get_job('powerbi_refresh')
                if job:
                    scheduler.pause_job('powerbi_refresh')
                    app.logger.info("Power BI refresh schedule paused")
                    
                    # Update saved configuration to paused
                    try:
                        schedule_config_file = 'powerbi_schedule_config.json'
                        if os.path.exists(schedule_config_file):
                            with open(schedule_config_file, 'r') as f:
                                config = json.load(f)
                            config['paused'] = True
                            config['paused_at'] = datetime.now().isoformat()
                            with open(schedule_config_file, 'w') as f:
                                json.dump(config, f, indent=2)
                            app.logger.info("Power BI schedule configuration updated to paused")
                    except Exception as e:
                        app.logger.error(f"Failed to update schedule configuration: {str(e)}")
                    
                    return jsonify({
                        'success': True,
                        'message': 'Power BI refresh schedule paused'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'No active schedule found'
                    })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Failed to pause schedule: {str(e)}'
                })
        else:
            return jsonify({
                'success': False,
                'error': 'No scheduler available'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/powerbi/resume-schedule', methods=['POST'])
def resume_powerbi_schedule():
    """Resume the paused Power BI refresh schedule"""
    global scheduler_active
    
    try:
        if scheduler and scheduler_active:
            try:
                job = scheduler.get_job('powerbi_refresh')
                if job:
                    scheduler.resume_job('powerbi_refresh')
                    app.logger.info("Power BI refresh schedule resumed")
                    
                    # Update saved configuration to resumed
                    try:
                        schedule_config_file = 'powerbi_schedule_config.json'
                        if os.path.exists(schedule_config_file):
                            with open(schedule_config_file, 'r') as f:
                                config = json.load(f)
                            config['paused'] = False
                            config['resumed_at'] = datetime.now().isoformat()
                            with open(schedule_config_file, 'w') as f:
                                json.dump(config, f, indent=2)
                            app.logger.info("Power BI schedule configuration updated to resumed")
                    except Exception as e:
                        app.logger.error(f"Failed to update schedule configuration: {str(e)}")
                    
                    return jsonify({
                        'success': True,
                        'message': 'Power BI refresh schedule resumed'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'No paused schedule found'
                    })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Failed to resume schedule: {str(e)}'
                })
        else:
            return jsonify({
                'success': False,
                'error': 'No scheduler available'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Auto-trigger Power BI refresh when loan data is saved
def trigger_powerbi_on_save():
    """Trigger Power BI refresh automatically when loan data is saved"""
    if POWERBI_AVAILABLE and powerbi_refresher:
        try:
            def run_auto_refresh():
                from powerbi_refresh import PowerBIRefresher
                refresher = PowerBIRefresher(
                    os.environ.get('POWERBI_USERNAME'),
                    os.environ.get('POWERBI_PASSWORD'), 
                    os.environ.get('POWERBI_DATASET_URL')
                )
                if hasattr(app, 'powerbi_notifications'):
                    refresher.add_notification_callback(app.powerbi_notifications.add_notification)
                app.logger.info("Auto-triggering Power BI refresh after loan data save")
                refresher.refresh_powerbi_dataset()
            
            refresh_thread = threading.Thread(target=run_auto_refresh)
            refresh_thread.daemon = True
            refresh_thread.start()
            
        except Exception as e:
            app.logger.warning(f"Auto Power BI refresh failed: {str(e)}")

# Scenario Comparison Routes
@app.route('/scenario-comparison')
def scenario_comparison_page():
    """Scenario comparison tool page"""
    return render_template('scenario_comparison.html')

@app.route('/api/powerbi/schedule-logs', methods=['GET'])
def get_schedule_logs():
    """Get Power BI schedule logs and statistics"""
    try:
        logs = []
        statistics = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'lastRun': None
        }
        
        # Read logs from powerbi_refresh.log if it exists
        log_file = 'powerbi_refresh.log'
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    log_lines = f.readlines()
                
                # Parse log lines (keep last 100 entries)
                for line in log_lines[-100:]:
                    if line.strip():
                        # Parse log format: timestamp - level - message
                        parts = line.strip().split(' - ', 2)
                        if len(parts) >= 3:
                            timestamp_str, level, message = parts
                            try:
                                # Try to parse timestamp
                                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                                logs.append({
                                    'timestamp': timestamp.isoformat(),
                                    'level': level.lower(),
                                    'message': message
                                })
                                
                                # Update statistics
                                statistics['total'] += 1
                                if 'success' in message.lower() or 'completed' in message.lower():
                                    statistics['successful'] += 1
                                elif 'error' in message.lower() or 'failed' in message.lower():
                                    statistics['failed'] += 1
                                    
                                if not statistics['lastRun'] or timestamp > datetime.fromisoformat(statistics['lastRun'].replace('Z', '+00:00')):
                                    statistics['lastRun'] = timestamp.isoformat()
                                    
                            except ValueError:
                                # If timestamp parsing fails, add with current time
                                logs.append({
                                    'timestamp': datetime.now().isoformat(),
                                    'level': 'info',
                                    'message': line.strip()
                                })
            except Exception as e:
                app.logger.error(f"Failed to read log file: {str(e)}")
        
        # Add some recent scheduler activity logs
        if scheduler and scheduler_active:
            try:
                job = scheduler.get_job('powerbi_refresh')
                if job:
                    logs.append({
                        'timestamp': datetime.now().isoformat(),
                        'level': 'info',
                        'message': f'Scheduler is active - Next run: {job.next_run_time}'
                    })
                    
                    # Load config for additional info
                    schedule_config_file = 'powerbi_schedule_config.json'
                    if os.path.exists(schedule_config_file):
                        with open(schedule_config_file, 'r') as f:
                            config = json.load(f)
                        
                        logs.append({
                            'timestamp': datetime.now().isoformat(),
                            'level': 'info',
                            'message': f'Schedule configuration: {config.get("interval", "unknown")} minute intervals'
                        })
                        
                        if config.get('paused'):
                            logs.append({
                                'timestamp': config.get('paused_at', datetime.now().isoformat()),
                                'level': 'warning',
                                'message': 'Schedule is currently paused'
                            })
            except Exception as e:
                app.logger.error(f"Failed to get scheduler info: {str(e)}")
        
        # Sort logs by timestamp (newest first)
        logs.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'success': True,
            'logs': logs,
            'statistics': statistics
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/powerbi/clear-logs', methods=['POST'])
def clear_schedule_logs():
    """Clear Power BI schedule logs"""
    try:
        log_file = 'powerbi_refresh.log'
        if os.path.exists(log_file):
            # Clear log file
            with open(log_file, 'w') as f:
                f.write('')
            app.logger.info("Power BI schedule logs cleared")
        
        return jsonify({
            'success': True,
            'message': 'Schedule logs cleared successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/powerbi/download-logs', methods=['GET'])
def download_schedule_logs():
    """Download Power BI schedule logs as a file"""
    try:
        from flask import send_file
        log_file = 'powerbi_refresh.log'
        if os.path.exists(log_file):
            return send_file(log_file, as_attachment=True, download_name=f'powerbi_schedule_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        else:
            # Create empty log file with header
            temp_content = f"Power BI Schedule Logs - Generated on {datetime.now().isoformat()}\n"
            temp_content += "No logs available.\n"
            
            with open('temp_logs.log', 'w') as f:
                f.write(temp_content)
            
            return send_file('temp_logs.log', as_attachment=True, download_name=f'powerbi_schedule_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/scenario-comparison/create', methods=['POST'])
@cross_origin()
def create_scenario_comparison():
    """Create a new scenario comparison"""
    try:
        data = request.get_json()
        comparison = create_scenario_comparison_from_request(data)
        
        # Calculate all scenarios
        comparison.calculate_all_scenarios()
        
        # Store in session for future access
        session['scenario_comparison'] = {
            'scenarios': comparison.scenarios,
            'created_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'comparison_table': comparison.get_comparison_table(),
            'best_scenario_analysis': comparison.get_best_scenario_analysis()
        })
        
    except Exception as e:
        app.logger.error(f"Scenario comparison creation failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/scenario-comparison/templates/<template_type>')
@cross_origin()
def get_scenario_templates(template_type):
    """Get predefined scenario templates"""
    try:
        # Get base parameters from request
        base_params = request.args.to_dict()
        
        # Convert string values to appropriate types
        for key in ['gross_amount', 'net_amount', 'annual_rate', 'loan_term', 'property_value']:
            if key in base_params:
                base_params[key] = float(base_params[key])
        
        # Generate templates based on type
        if template_type == 'interest_rates':
            rates = [10, 12, 15, 18]
            scenarios = ScenarioTemplates.interest_rate_comparison(base_params, rates)
        elif template_type == 'loan_terms':
            terms = [6, 12, 18, 24]
            scenarios = ScenarioTemplates.loan_term_comparison(base_params, terms)
        elif template_type == 'repayment_options':
            scenarios = ScenarioTemplates.repayment_option_comparison(base_params)
        elif template_type == 'loan_amounts':
            amounts = [500000, 750000, 1000000, 1500000]
            scenarios = ScenarioTemplates.loan_amount_comparison(base_params, amounts)
        else:
            return jsonify({
                'success': False,
                'error': f'Unknown template type: {template_type}'
            }), 400
        
        return jsonify({
            'success': True,
            'scenarios': scenarios
        })
        
    except Exception as e:
        app.logger.error(f"Template generation failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/scenario-comparison/export')
@cross_origin()
def export_scenario_comparison():
    """Export scenario comparison data"""
    try:
        comparison_data = session.get('scenario_comparison')
        if not comparison_data:
            return jsonify({
                'success': False,
                'error': 'No scenario comparison data found'
            }), 404
        
        # Recreate comparison object
        comparison = ScenarioComparison()
        for scenario_data in comparison_data['scenarios']:
            comparison.scenarios.append(scenario_data)
        
        # Export as JSON
        export_data = comparison.export_comparison()
        
        return jsonify({
            'success': True,
            'export_data': export_data
        })
        
    except Exception as e:
        app.logger.error(f"Scenario comparison export failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


