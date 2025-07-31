# Loan Calculation Logic Guide

## 🎯 Navigation Overview

This document provides a comprehensive map of all calculation logic in the Novellus Loan Management System with color-coded sections for easy navigation and modification.

---

## 📁 File Structure Overview

### Core Calculation Files
- **`calculations.py`** - Main calculation engine with all loan type logic
- **`routes.py`** - API endpoints and parameter handling  
- **`excel_generator.py`** - Excel export calculations
- **`professional_quote_generator.py`** - PDF/DOCX quote calculations

---

## 🔵 **BRIDGE LOANS** - Main Calculation Logic

### 📍 Location: `calculations.py` - Lines 50-200

#### 🟢 **Bridge Loan Entry Point**
```python
def calculate_bridge_loan(gross_amount, interest_rate, loan_term, ...)
    # Main bridge loan calculation dispatcher
    # Location: calculations.py:50-80
```

#### 🟠 **Repayment Type Functions**

##### 🔴 **Interest Retained (none)**
```python
def _calculate_bridge_retained_interest(gross_amount, interest_rate, loan_term_days, ...)
    # Formula: Interest = (Gross × Rate × Days) / (365 × 100)
    # Net Advance = Gross - All Fees - Interest
    # Location: calculations.py:85-120
```

##### 🟡 **Service Only (interest_only)**  
```python
def _calculate_bridge_interest_only(gross_amount, interest_rate, loan_term_days, ...)
    # Formula: Interest = (Gross × Rate × Days) / (365 × 100)
    # Net Advance = Gross - Fees Only (no interest deduction)
    # Location: calculations.py:125-160
```

##### 🟢 **Service + Capital (service_and_capital)**
```python
def _calculate_bridge_service_capital(gross_amount, interest_rate, loan_term_days, capital_repayment, ...)
    # Uses declining balance methodology
    # Monthly interest calculated on reducing principal
    # Location: calculations.py:165-220
```

##### 🔵 **Flexible Payment (flexible_payment)**
```python
def _calculate_bridge_flexible(gross_amount, interest_rate, loan_term_days, flexible_payment, ...)
    # Similar to service_capital but with user-defined payment amounts
    # Declining balance with flexible payment schedule
    # Location: calculations.py:225-280
```

##### 🟣 **Capital Payment Only (capital_payment_only)**
```python
def _calculate_bridge_capital_only(gross_amount, interest_rate, loan_term_days, capital_repayment, ...)
    # Retains full interest upfront like retained interest
    # Provides proportional refund based on capital payments
    # Location: calculations.py:285-330
```

#### 🔶 **Net-to-Gross Conversion**
```python
def _calculate_gross_from_net_bridge(net_amount, ...)
    # Excel-compatible formulas for net-to-gross conversion
    # Different formulas per repayment type
    # Location: calculations.py:335-420
```

---

## 🟠 **TERM LOANS** - Main Calculation Logic

### 📍 Location: `calculations.py` - Lines 450-650

#### 🟢 **Term Loan Entry Point**
```python
def calculate_term_loan(gross_amount, interest_rate, loan_term, ...)
    # Main term loan calculation dispatcher
    # Location: calculations.py:450-480
```

#### 🟠 **Repayment Type Functions**

##### 🔴 **Interest Retained (none)**
```python
def _calculate_term_retained_interest(gross_amount, interest_rate, loan_term_days, ...)
    # Formula: Interest = (Gross × Rate × Days) / (365 × 100)
    # Net Advance = Gross - All Fees - Interest
    # Location: calculations.py:485-520
```

##### 🟡 **Service Only (interest_only)**
```python
def _calculate_term_interest_only(gross_amount, interest_rate, loan_term_days, ...)
    # Formula: Interest = (Gross × Rate × Days) / (365 × 100)
    # Net Advance = Gross - Fees Only
    # Location: calculations.py:525-560
```

##### 🟢 **Service + Capital (service_and_capital)**
```python
def _calculate_term_service_capital(gross_amount, interest_rate, loan_term_days, capital_repayment, ...)
    # Sophisticated amortization methodology
    # Monthly payments with principal/interest split
    # Location: calculations.py:565-620
```

##### 🔵 **Flexible Payment (flexible_payment)**
```python
def _calculate_term_flexible(gross_amount, interest_rate, loan_term_days, flexible_payment, ...)
    # User-defined payment amounts with amortization
    # Location: calculations.py:625-670
```

##### 🟣 **Capital Payment Only (capital_payment_only)**
```python
def _calculate_term_capital_only(gross_amount, interest_rate, loan_term_days, capital_repayment, ...)
    # Retains full interest upfront with proportional refund
    # Location: calculations.py:675-720
```

---

## 🟢 **DEVELOPMENT LOANS** - Main Calculation Logic

### 📍 Location: `calculations.py` - Lines 750-1100

#### 🟢 **Development Loan Entry Point**
```python
def calculate_development_loan(net_amount, interest_rate, loan_term, tranches, ...)
    # Main development loan calculation with Goal Seek methodology
    # Location: calculations.py:750-800
```

#### 🔶 **Goal Seek Algorithm**
```python
def _calculate_development_goal_seek(net_amount, ...)
    # Iterative algorithm to find gross amount
    # Formula: Gross = (Net + Fees + Interest) / 0.98
    # Converges with £0.01 precision
    # Location: calculations.py:805-880
```

#### 🟡 **Interest Calculation - Excel Methodology**
```python
def _calculate_development_interest_excel_exact(gross_amount, tranches, ...)
    # Compound daily interest calculation
    # Day 1 advance + Monthly tranche releases
    # Uses 30.4375 days per month (365/12)
    # Location: calculations.py:885-950
```

#### 🔵 **Monthly Compound Breakdown**
```python
def _generate_monthly_compound_breakdown(...)
    # Detailed month-by-month interest calculation
    # Shows tranche releases and compound daily interest
    # Location: calculations.py:955-1020
```

#### 🟠 **Tranche Processing**
```python
def _process_user_tranches(user_tranches, ...)
    # Handles user-defined tranche amounts and timing
    # Validates and processes tranche data
    # Location: calculations.py:1025-1080
```

---

## 🟣 **DEVELOPMENT 2 LOANS** - Enhanced Development Logic

### 📍 Location: `calculations.py` - Lines 1150-1350

#### 🟢 **Development 2 Entry Point**
```python
def calculate_development2_loan(net_amount, interest_rate, loan_term, tranches, ...)
    # Enhanced development loan with flexible tranche count
    # Location: calculations.py:1150-1200
```

#### 🔶 **Dynamic Tranche Handling**
```python
def _process_development2_tranches(user_tranches, ...)
    # Supports any number of tranches (not limited to 10)
    # Dynamic tranche timing and amount processing
    # Location: calculations.py:1205-1270
```

---

## 🔷 **PAYMENT SCHEDULE GENERATION**

### 📍 Location: `calculations.py` - Lines 1400-1800

#### 🟢 **Main Schedule Generator**
```python
def _generate_detailed_payment_schedule(loan_type, repayment_option, ...)
    # Universal payment schedule generator for all loan types
    # Location: calculations.py:1400-1450
```

#### 🟠 **Bridge Schedule Generation**
```python
def _generate_detailed_bridge_schedule(repayment_option, ...)
    # Bridge-specific payment schedule logic
    # Handles all bridge repayment types
    # Location: calculations.py:1455-1580
```

#### 🟡 **Term Schedule Generation**
```python
def _generate_detailed_term_schedule(repayment_option, ...)
    # Term-specific payment schedule logic
    # Sophisticated amortization calculations
    # Location: calculations.py:1585-1710
```

#### 🔵 **Development Schedule Generation**
```python
def _generate_development_schedule(...)
    # Development loan payment schedule
    # Tranche release tracking and compound interest
    # Location: calculations.py:1715-1840
```

---

## 🔶 **NET-TO-GROSS CONVERSIONS**

### 📍 Location: `calculations.py` - Lines 1900-2200

#### 🔴 **Excel-Compatible Formulas**

##### Bridge/Term Net-to-Gross
```python
# Interest Retained Formula
Gross = (Net + Legal Fees) / (1 - Arrangement Fee - Title Insurance - (Interest Rate × Months/12)/100)

# Service Only/Service+Capital Formula  
Gross = (Net + Legal Fees) / (1 - Arrangement Fee - Title Insurance)

# Flexible Payment Formula
Gross = (Net + Legal Fees) / (1 - Arrangement Fee - Title Insurance - (months interest))
```

##### Development Net-to-Gross
```python
# Goal Seek Formula
Gross = (Net + All Fees + Compound Daily Interest) / 0.98
```

---

## 🔷 **API ROUTES AND PARAMETER HANDLING**

### 📍 Location: `routes.py` - Lines 50-400

#### 🟢 **Main Calculation Route**
```python
@app.route('/calculate', methods=['POST'])
def calculate():
    # Main API endpoint for all loan calculations
    # Parameter extraction and validation
    # Location: routes.py:50-100
```

#### 🟠 **Parameter Processing**
```python
def extract_calculation_parameters(request):
    # Handles both camelCase and snake_case parameters
    # Safe conversion functions (safe_float, safe_int)
    # Location: routes.py:105-180
```

#### 🔵 **Field Mapping Functions**
```python
def _build_bridge_loan_result(result, ...):
def _build_term_loan_result(result, ...):
def _build_development_loan_result(result, ...):
    # Maps calculation results to frontend-compatible format
    # Location: routes.py:185-350
```

---

## 🔶 **EXPORT SYSTEM REMOVED**

### 🚫 **Export Functionality Eliminated**
All export functionality (Excel, PDF, DOCX) has been completely removed from the application:
- **Excel Generator**: `excel_generator.py` - **REMOVED**
- **Professional Quote**: `professional_quote_generator.py` - **REMOVED**  
- **PDF Generator**: `pdf_quote_generator.py` - **REMOVED**
- **Export Routes**: All `/download-*` and `/generate-*` routes - **REMOVED**
- **Export Buttons**: All export buttons from UI - **REMOVED**

### 🔄 **Edit Functionality Added**
#### 🟢 **Loan Editing System**
```python
# Location: templates/loan_history.html:520-580
def editLoan():
    # Redirects to calculator with pre-populated loan data
    # Allows recalculation and saving of changes

def buildEditParams(loan):
    # Maps saved loan data to calculator form parameters
    # Handles all loan types and input variations
```

---

## 🎨 **MODIFICATION GUIDE**

### 🔴 **To Modify Interest Calculations:**
1. **Bridge/Term**: Edit functions in `calculations.py` lines 85-330 (bridge) or 485-720 (term)
2. **Development**: Edit `_calculate_development_interest_excel_exact()` in lines 885-950
3. **Update corresponding payment schedule generators**

### 🟡 **To Modify Net-to-Gross Formulas:**
1. **Bridge**: Edit `_calculate_gross_from_net_bridge()` in lines 335-420
2. **Term**: Edit `_calculate_gross_from_net_term()` in lines 725-810  
3. **Development**: Edit Goal Seek algorithm in lines 805-880

### 🟢 **To Add New Repayment Types:**
1. Add new function in appropriate loan type section
2. Update main dispatcher function (e.g., `calculate_bridge_loan()`)
3. Add corresponding payment schedule logic
4. Update field mapping in `routes.py`

### 🔵 **To Modify Payment Schedules:**
1. Edit `_generate_detailed_[loan_type]_schedule()` functions in lines 1455-1840
2. Update Excel export sheet generators if needed
3. Test with different repayment types

### 🟠 **To Change Fee Calculations:**
1. **Arrangement Fee**: Search for `arrangement_fee` in `calculations.py`
2. **Title Insurance**: Search for `title_insurance` calculations
3. **Legal/Site Fees**: Usually added as fixed amounts

### 🟣 **To Modify Date Sensitivity:**
1. **Loan Term Days**: Search for `loan_term_days` parameter usage
2. **Date Calculations**: Edit date handling in main calculation functions
3. **Priority Systems**: Check Priority 1 (user dates) vs Priority 2 (calculated dates)

---

## 🔍 **Quick Search Patterns**

### Find Specific Calculations:
- **Interest formulas**: Search `(gross_amount * interest_rate * loan_term_days)`
- **Net advance**: Search `net_advance =` or `netAdvance`
- **Fee calculations**: Search `arrangement_fee` or `title_insurance`
- **Payment schedules**: Search `_generate_detailed_` or `payment_schedule`

### Find Specific Loan Types:
- **Bridge**: Search `calculate_bridge` or `bridge_loan`
- **Term**: Search `calculate_term` or `term_loan` 
- **Development**: Search `calculate_development` or `goal_seek`
- **Development 2**: Search `calculate_development2`

### Find Edit Logic:
- **Loan Editing**: Search `editLoan` in `loan_history.html`
- **Parameter Building**: Search `buildEditParams` in `loan_history.html`
- **Field mapping**: Search `_build_` in `routes.py`

---

## ⚠️ **Critical Modification Points**

### 🔴 **High Impact Changes** (Test Thoroughly):
1. **Interest calculation formulas** - affects all calculations
2. **Net-to-Gross conversions** - affects gross amount results
3. **Goal Seek algorithm** - affects development loan accuracy
4. **Payment schedule generation** - affects detailed breakdowns

### 🟡 **Medium Impact Changes**:
1. **Fee calculation methods** - affects net advance
2. **Date handling logic** - affects term sensitivity
3. **Field mapping functions** - affects frontend display

### 🟢 **Low Impact Changes**:
1. **Display formatting** - visual changes only
2. **Export styling** - Excel/DOCX appearance
3. **Validation messages** - user experience improvements

---

## 📚 **Testing Guidelines**

After any calculation modifications:

1. **Run comprehensive tests** with multiple loan scenarios
2. **Verify Excel accuracy** against known working examples
3. **Check all repayment types** for the modified loan type
4. **Test both gross-to-net and net-to-gross** directions
5. **Validate payment schedules** match calculation results
6. **Test export functions** (Excel/DOCX) with new calculations

---

*This guide provides a complete map of the calculation logic. Use the color coding and line numbers to quickly navigate to specific sections for modifications.*