# Novellus Loan Management System - Technical Documentation

## Overview
This comprehensive guide covers all loan calculation types, debugging procedures, and maintenance protocols for the Novellus Loan Management System.

## System Architecture

### Core Components
1. **Frontend**: Bootstrap 5 + Vanilla JavaScript (`templates/calculator.html`, `static/js/calculator.js`)
2. **Backend API**: Flask routes (`routes.py`)
3. **Calculation Engine**: Core logic (`calculations.py`)
4. **Export Generators**: Professional documents (`professional_quote_generator.py`, `excel_generator.py`)
5. **Database Models**: SQLAlchemy ORM (`models.py`)

### Data Flow
```
Frontend Form → Routes.py → Calculations.py → Results → Frontend Display
                     ↓
                Export Generators (PDF/Excel)
```

## Loan Calculation Types

### 1. Bridge Loans
**Purpose**: Short-term financing for property transactions

#### Repayment Options:
- **Retained Interest** (`repayment_option="none"`): Interest deducted upfront
- **Service Only** (`repayment_option="service_only"`): Interest-only payments
- **Service + Capital** (`repayment_option="service_and_capital"`): Principal + interest payments
- **Flexible Payment** (`repayment_option="flexible_payment"`): Custom payment amounts

#### Key Calculation Methods:
- `_calculate_bridge_retained()` - Retained interest with upfront deduction
- `_calculate_bridge_interest_only()` - Monthly interest payments
- `_calculate_bridge_service_capital()` - Declining balance with principal payments
- `_calculate_bridge_flexible()` - Custom payment with declining balance

#### Net Advance Formula:
- **Retained Interest**: `Gross Amount - All Fees - Total Interest`
- **Non-Retained**: `Gross Amount` (fees tracked separately)

### 2. Term Loans
**Purpose**: Long-term property financing with structured repayment

#### Repayment Options:
- **Retained Interest** (`repayment_option="none"`): Interest deducted upfront
- **Service Only** (`repayment_option="service_only"`): Interest-only payments
- **Service + Capital** (`repayment_option="service_and_capital"`): Amortizing payments
- **Flexible Payment** (`repayment_option="flexible_payment"`): Custom payment amounts

#### Key Calculation Methods:
- `_calculate_term_retained()` - Retained interest calculation
- `_calculate_term_interest_only()` - Monthly interest-only payments
- `_calculate_term_service_capital()` - User-specified capital repayment
- `_calculate_term_flexible()` - Custom payment schedule

#### Interest Calculation:
- Uses daily interest methodology: `loan_term_days / 365`
- Date-sensitive calculations based on actual calendar days

### 3. Development Loans
**Purpose**: Construction/development project financing with tranche releases

#### Features:
- **Net-to-Gross Calculation**: Users enter net amount needed, system calculates gross
- **Tranche Structure**: Multiple releases over development period
- **Compound Daily Interest**: Excel-compatible methodology
- **Iterative Arrangement Fee**: Convergent calculation for exact 2%

#### Key Calculation Methods:
- `calculate_development_loan()` - Main calculation logic
- `_generate_development_schedule()` - Payment schedule creation
- `_calculate_monthly_compound_interest()` - Compound daily interest breakdown

#### Net Advance Formula:
- **Always Retained**: `Gross Amount - All Fees - Total Interest`

#### Special Features:
- Day 1 Advance calculation with user input
- Progressive tranche releases (£70k standard)
- Compound daily interest: `Balance × (1 + daily_rate)^days`
- Excel methodology compatibility with 30.4 days/month precision

## Debugging Procedures

### 1. Calculation Issues

#### Step 1: Check Logs
```bash
# View application logs
tail -f /tmp/gunicorn.log

# Key log patterns to look for:
INFO:root:Routes - Interest rate extraction
INFO:app:ROUTES.PY RETAINED INTEREST NET ADVANCE
INFO:root:Using USER tranches
```

#### Step 2: Verify Input Parameters
- Check `routes.py` parameter extraction
- Verify field mapping between frontend and backend
- Confirm data types (Decimal vs float)

#### Step 3: Trace Calculation Flow
1. `routes.py` - Parameter extraction and validation
2. `calculations.py` - Core calculation logic
3. `routes.py` - Result processing and field mapping
4. Frontend display

#### Common Issues:
- **Field Mapping**: `grossAmount` vs `gross_amount`
- **Data Types**: Decimal/float type mixing
- **Parameter Passing**: Missing or incorrect loan_term_days
- **Date Handling**: String vs datetime conversion

### 2. Frontend Issues

#### JavaScript Debugging:
```javascript
// Enable console logging
console.log("Form data collected:", formData);
console.log("Results received:", data);

// Check field mapping
console.log("Currency replacement debug:", {
    currentSymbol: currencySymbol,
    originalValue: originalValue,
    fixedValue: fixedValue
});
```

#### Common Problems:
- Currency symbol replacement
- Field visibility toggle
- Table rendering issues
- Date synchronization

### 3. Export Generation Issues

#### PDF/DOCX Problems:
- Check field mapping in generators
- Verify calculation result structure
- Test with minimal data set

#### Excel Issues:
- Formula validation
- Cell formatting problems
- Sheet structure issues

## Maintenance Procedures

### 1. Adding New Loan Types

#### Step 1: Backend Calculation
1. Add calculation method to `calculations.py`
2. Add route handler in `routes.py`
3. Update field mapping logic

#### Step 2: Frontend Integration
1. Add loan type option to `calculator.html`
2. Update JavaScript handling in `calculator.js`
3. Test all repayment options

#### Step 3: Export Support
1. Add templates to `professional_quote_generator.py`
2. Update Excel sheets in `excel_generator.py`
3. Test document generation

### 2. Modifying Calculation Logic

#### Critical Steps:
1. **Always backup current logic**
2. **Test with known reference values**
3. **Verify all repayment options**
4. **Update documentation**

#### Testing Protocol:
```python
# Test framework in calculations.py
def test_calculation(loan_type, amount, rate, term):
    result = calculate_loan(loan_type, amount, rate, term)
    assert result['grossAmount'] > 0
    assert result['totalInterest'] > 0
    return result
```

### 3. Database Maintenance

#### Regular Tasks:
1. Monitor session storage usage
2. Clean up old calculation results
3. Backup user preferences
4. Update model relationships

### 4. Performance Optimization

#### Key Areas:
1. **Calculation Caching**: Cache complex calculations
2. **Database Queries**: Optimize loan retrieval
3. **File Generation**: Stream large documents
4. **Frontend Optimization**: Minimize JavaScript execution

## Configuration Management

### Environment Variables
```bash
DATABASE_URL=postgresql://...
SESSION_SECRET=your_secret_key
UPLOAD_FOLDER=uploads/
```

### Key Settings
- `calculations.py`: Precision settings (Decimal places)
- `routes.py`: Field mapping configuration
- `templates/`: UI customization

## Error Handling

### Common Error Patterns

#### 1. Calculation Errors
```python
try:
    result = calculate_loan(...)
except DecimalException as e:
    app.logger.error(f"Calculation error: {e}")
    return {"error": "Invalid calculation parameters"}
```

#### 2. Field Mapping Errors
```python
def safe_get(data, field, default=0):
    """Safely extract field with fallback"""
    return data.get(field, data.get(snake_case(field), default))
```

#### 3. Date Handling Errors
```python
def parse_date(date_str):
    """Convert string to datetime with error handling"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return datetime.now()
```

## Testing Strategy

### 1. Unit Testing
- Individual calculation methods
- Field mapping functions
- Date conversion utilities

### 2. Integration Testing
- End-to-end loan calculations
- Export generation pipeline
- Database operations

### 3. User Acceptance Testing
- Test all loan types
- Verify calculations against Excel
- Test document exports

## Troubleshooting Quick Reference

### Issue: Total Net Advance Incorrect
**Solution**: Check repayment option logic in `routes.py` lines 290-310

### Issue: Interest Calculation Wrong
**Solution**: Verify `loan_term_days` parameter passing and date handling

### Issue: Frontend Not Updating
**Solution**: Check JavaScript console for errors, verify field mapping

### Issue: Export Generation Fails
**Solution**: Test calculation results structure, check field mapping in generators

### Issue: Development Loan Tranche Problems
**Solution**: Verify user tranche parsing and compound interest calculation

## Support Contacts
- System Administrator: Check logs first
- Database Issues: Verify connection and model relationships  
- Calculation Issues: Reference this guide and check precision settings