import os
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from werkzeug.utils import secure_filename
from flask import current_app
import csv
import io

def allowed_file(filename: str, allowed_extensions: set = None) -> bool:
    """Check if file extension is allowed"""
    if allowed_extensions is None:
        allowed_extensions = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'gif'}
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def secure_upload_filename(filename: str) -> str:
    """Generate secure filename for uploads"""
    # Get file extension
    ext = ''
    if '.' in filename:
        ext = '.' + filename.rsplit('.', 1)[1].lower()
    
    # Generate unique filename
    unique_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    return f"{timestamp}_{unique_id}{ext}"

def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA256 hash of file"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def format_currency(amount: float, currency: str = 'GBP') -> str:
    """Format currency amount with appropriate symbol"""
    symbols = {
        'GBP': '£',
        'EUR': '€',
        'USD': '$'
    }
    symbol = symbols.get(currency, '£')
    return f"{symbol}{amount:,.2f}"

def format_percentage(value: float, decimal_places: int = 2) -> str:
    """Format percentage value"""
    return f"{value:.{decimal_places}f}%"

def validate_loan_application_data(data: Dict[str, Any]) -> List[str]:
    """Validate loan application data and return list of errors"""
    errors = []
    
    # Required fields
    required_fields = [
        'loan_type', 'property_address', 'property_value',
        'loan_amount', 'loan_term'
    ]
    
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"{field.replace('_', ' ').title()} is required")
    
    # Numeric validations
    if 'property_value' in data:
        try:
            value = float(data['property_value'])
            if value <= 0:
                errors.append("Property value must be greater than 0")
        except (ValueError, TypeError):
            errors.append("Property value must be a valid number")
    
    if 'loan_amount' in data:
        try:
            value = float(data['loan_amount'])
            if value <= 0:
                errors.append("Loan amount must be greater than 0")
        except (ValueError, TypeError):
            errors.append("Loan amount must be a valid number")
    
    if 'loan_term' in data:
        try:
            value = int(data['loan_term'])
            if value < 3:
                errors.append("Loan term must be at least 3 months")
            if value > 600:
                errors.append("Loan term cannot exceed 600 months")
        except (ValueError, TypeError):
            errors.append("Loan term must be a valid number")
    
    # LTV validation
    if 'property_value' in data and 'loan_amount' in data:
        try:
            ltv = (float(data['loan_amount']) / float(data['property_value'])) * 100
            if ltv > 95:
                errors.append("LTV ratio cannot exceed 95%")
        except (ValueError, TypeError, ZeroDivisionError):
            pass  # Skip if values are invalid
    
    return errors

def validate_quote_data(data: Dict[str, Any]) -> List[str]:
    """Validate quote data and return list of errors"""
    errors = []
    
    # Required fields
    required_fields = [
        'gross_amount', 'interest_rate', 'loan_term'
    ]
    
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"{field.replace('_', ' ').title()} is required")
    
    # Numeric validations
    if 'interest_rate' in data:
        try:
            rate = float(data['interest_rate'])
            if rate <= 0 or rate > 50:
                errors.append("Interest rate must be between 0% and 50%")
        except (ValueError, TypeError):
            errors.append("Interest rate must be a valid number")
    
    return errors

def generate_payment_schedule_csv(schedule: List[Dict], currency: str = 'GBP') -> str:
    """Generate CSV string from payment schedule"""
    output = io.StringIO()
    
    if not schedule:
        return ""
    
    # Determine if this is a detailed schedule (with dates)
    has_dates = 'start_date' in schedule[0]
    
    if has_dates:
        fieldnames = ["Period", "Start", "End", "Days", "Opening Balance", 
                     "Daily Rate", "Interest", "Capital", "Total Payment", "Closing Balance"]
    else:
        fieldnames = ["Month", "Payment", "Principal", "Interest", "Balance"]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    symbol = '£' if currency == 'GBP' else '€' if currency == 'EUR' else '$'
    
    for payment in schedule:
        # Handle both 'month' and 'period' fields for compatibility
        period_value = payment.get('month', payment.get('period', 1))
        
        if has_dates:
            row = {
                "Period": period_value,
                "Start": payment.get('start_date', '').strftime('%d/%m/%Y') if payment.get('start_date') else '',
                "End": payment.get('end_date', '').strftime('%d/%m/%Y') if payment.get('end_date') else '',
                "Days": payment.get('days', ''),
                "Opening Balance": f"{symbol}{payment.get('opening_balance', payment.get('balance', 0)) + payment.get('principal', 0):.2f}",
                "Daily Rate": f"{payment.get('daily_rate', 0) * 100:.8f}%" if payment.get('daily_rate') else '',
                "Interest": f"{symbol}{payment.get('interest', 0):.2f}",
                "Capital": f"{symbol}{payment.get('principal', 0):.2f}",
                "Total Payment": f"{symbol}{payment.get('payment', payment.get('total_payment', 0)):.2f}",
                "Closing Balance": f"{symbol}{payment.get('balance', payment.get('closing_balance', 0)):.2f}"
            }
        else:
            row = {
                "Month": period_value,
                "Payment": f"{symbol}{payment.get('payment', payment.get('total_payment', 0)):.2f}",
                "Principal": f"{symbol}{payment.get('principal', 0):.2f}",
                "Interest": f"{symbol}{payment.get('interest', 0):.2f}",
                "Balance": f"{symbol}{payment.get('balance', payment.get('closing_balance', 0)):.2f}"
            }
        
        writer.writerow(row)
    
    csv_content = output.getvalue()
    output.close()
    return csv_content

def calculate_ltv(loan_amount: float, property_value: float) -> float:
    """Calculate Loan to Value ratio"""
    if property_value <= 0:
        return 0
    return (loan_amount / property_value) * 100

def get_currency_symbol(currency: str) -> str:
    """Get currency symbol"""
    symbols = {
        'GBP': '£',
        'EUR': '€',
        'USD': '$'
    }
    return symbols.get(currency.upper(), '£')

def parse_currency_amount(amount_str: str) -> float:
    """Parse currency string to float"""
    if not amount_str:
        return 0.0
    
    # Remove currency symbols and commas
    cleaned = amount_str.replace('£', '').replace('€', '').replace('$', '').replace(',', '').strip()
    
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

def generate_application_reference() -> str:
    """Generate unique application reference"""
    timestamp = datetime.now().strftime('%Y%m%d')
    random_part = str(uuid.uuid4())[:8].upper()
    return f"NOV-{timestamp}-{random_part}"

def calculate_days_between_dates(start_date: datetime, end_date: datetime) -> int:
    """Calculate days between two dates"""
    return (end_date - start_date).days

def add_business_days(start_date: datetime, business_days: int) -> datetime:
    """Add business days to a date (excluding weekends)"""
    current_date = start_date
    days_added = 0
    
    while days_added < business_days:
        current_date += timedelta(days=1)
        # Check if it's a weekday (Monday = 0, Sunday = 6)
        if current_date.weekday() < 5:
            days_added += 1
    
    return current_date

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove or replace unsafe characters
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    name, ext = os.path.splitext(filename)
    if len(name) > 100:
        name = name[:100]
    
    return name + ext

def get_file_size_mb(file_path: str) -> float:
    """Get file size in megabytes"""
    if os.path.exists(file_path):
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    return 0

def validate_email(email: str) -> bool:
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """Basic phone validation"""
    import re
    # Remove spaces, hyphens, parentheses
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    # Check if it's all digits and reasonable length
    return cleaned.isdigit() and 10 <= len(cleaned) <= 15

def format_date(date: datetime, format_str: str = '%d/%m/%Y') -> str:
    """Format date to string"""
    if isinstance(date, datetime):
        return date.strftime(format_str)
    return str(date)

def parse_date(date_str: str, format_str: str = '%Y-%m-%d') -> Optional[datetime]:
    """Parse date string to datetime"""
    try:
        return datetime.strptime(date_str, format_str)
    except (ValueError, TypeError):
        return None
