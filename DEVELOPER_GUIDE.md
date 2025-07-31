# Novellus Loan Calculator - Complete Developer Guide

## Table of Contents

1. [Input Field Architecture & Data Flow](#input-field-architecture--data-flow)
2. [Date & Period Management System](#date--period-management-system)
3. [Complete Field Lineage Documentation](#complete-field-lineage-documentation)
4. [Loan Type & Repayment Calculation Logic](#loan-type--repayment-calculation-logic)
5. [Output Modification Guide](#output-modification-guide)
6. [Advanced Customization](#advanced-customization)

---

## 1. Input Field Architecture & Data Flow

### Frontend Form Fields Location
**File**: `templates/calculator.html` (Lines 427-800)

### Core Input Fields Structure

#### A. Loan Identification Fields
```html
<!-- Loan Name (Line 433) -->
<input type="text" class="form-control" id="loanName" name="loanName">
- JavaScript Access: document.getElementById('loanName').value
- Storage Variable: formData.loanName
- Backend Parameter: data.get('loanName')
- Modification Location: templates/calculator.html:433
```

#### B. Loan Configuration Fields
```html
<!-- Loan Type (Line 445) -->
<select class="form-select" id="loanType" name="loan_type">
- JavaScript Access: document.getElementById('loanType').value
- Storage Variable: formData.loan_type
- Backend Parameter: data.get('loan_type')
- Options: 'bridge', 'term', 'development', 'development2'
- Modification Location: templates/calculator.html:445-450

<!-- Repayment Option (Line 456) -->
<select class="form-select" id="repaymentOption" name="repayment_option">
- JavaScript Access: document.getElementById('repaymentOption').value
- Storage Variable: formData.repayment_option
- Backend Parameter: data.get('repayment_option')
- Dynamic Options Based on Loan Type
- Modification Location: templates/calculator.html:456-462
```

#### C. Financial Fields
```html
<!-- Property Value (Line 479) -->
<input type="number" id="propertyValue" name="property_value">
- JavaScript Access: parseFloat(document.getElementById('propertyValue').value)
- Storage Variable: formData.property_value
- Backend Parameter: float(data.get('property_value', 0))
- Currency Symbol: Updates via updateCurrencySymbols() function

<!-- Gross Amount (Line 509) -->
<input type="number" id="grossAmountFixed" name="gross_amount">
- JavaScript Access: parseFloat(document.getElementById('grossAmountFixed').value)
- Storage Variable: formData.gross_amount
- Backend Parameter: float(data.get('gross_amount', 0))
- Toggle Logic: Controlled by amount_input_type radio buttons

<!-- Net Amount (Line 525) -->
<input type="number" id="netAmountInput" name="net_amount">
- JavaScript Access: parseFloat(document.getElementById('netAmountInput').value)
- Storage Variable: formData.net_amount
- Backend Parameter: float(data.get('net_amount', 0))
- Visibility: Controlled by JavaScript toggleAmountInputType()
```

#### D. Interest & Term Fields
```html
<!-- Interest Rate (Line 580) -->
<input type="number" id="annualRate" name="interest_rate">
- JavaScript Access: parseFloat(document.getElementById('annualRate').value)
- Storage Variable: formData.interest_rate
- Backend Parameter: float(data.get('interest_rate', 12))
- Toggle Logic: Monthly vs Annual rate conversion

<!-- Loan Term (Line 625) -->
<input type="number" id="loanTerm" name="loan_term">
- JavaScript Access: parseInt(document.getElementById('loanTerm').value)
- Storage Variable: formData.loan_term
- Backend Parameter: int(data.get('loan_term', 12))
- Unit: Controlled by loanTermUnit dropdown
```

### JavaScript Data Collection Function
**File**: `static/js/calculator.js` (Lines 2500+)
```javascript
collectFormData() {
    return {
        loanName: document.getElementById('loanName').value,
        loan_type: document.getElementById('loanType').value,
        repayment_option: document.getElementById('repaymentOption').value,
        currency: document.getElementById('currency').value,
        property_value: parseFloat(document.getElementById('propertyValue').value) || 0,
        gross_amount: parseFloat(document.getElementById('grossAmountFixed').value) || 0,
        net_amount: parseFloat(document.getElementById('netAmountInput').value) || 0,
        interest_rate: parseFloat(document.getElementById('annualRate').value) || 12,
        loan_term: parseInt(document.getElementById('loanTerm').value) || 12
        // ... additional fields
    };
}
```

### Backend Data Processing
**File**: `routes.py` (Lines 120-180)
```python
@app.route('/api/calculate', methods=['POST'])
def calculate_loan():
    data = request.get_json() or {}
    
    # Extract and validate parameters
    loan_type = data.get('loan_type', 'bridge')
    gross_amount = float(data.get('gross_amount', 0) or 0)
    net_amount = float(data.get('net_amount', 0) or 0)
    property_value = float(data.get('property_value', 0) or 0)
    interest_rate = float(data.get('interest_rate', 12) or 12)
    loan_term = int(data.get('loan_term', 12) or 12)
    
    # Pass to calculation engine
    calculator = SimpleLoanCalculator()
    if loan_type == 'bridge':
        result = calculator.calculate_bridge_loan(data)
    elif loan_type == 'term':
        result = calculator.calculate_term_loan(data)
    elif loan_type in ['development', 'development2']:
        result = calculator.calculate_development_loan(data)
```

---

## 2. Date & Period Management System

### Date Field Implementation
**File**: `templates/calculator.html` (Lines 640-680)

#### Start Date Field
```html
<input type="date" id="startDate" name="start_date">
- Default Value: Current date (set by setDefaultDate())
- JavaScript Handler: addEventListener('change', calculateEndDate)
- Modification Location: templates/calculator.html:642
```

#### End Date Field
```html
<input type="date" id="endDate" name="end_date">
- Calculated Value: Based on start_date + loan_term
- JavaScript Handler: addEventListener('change', recalculateLoanTerm)
- Editable: Click to make manually editable
- Modification Location: templates/calculator.html:650
```

### Date Calculation Logic
**File**: `templates/calculator.html` (Lines 1090-1180)

#### Forward Calculation (Start Date + Term → End Date)
```javascript
function calculateEndDate() {
    const startDate = document.getElementById('startDate').value;
    const loanTerm = parseInt(document.getElementById('loanTerm').value);
    const loanTermUnit = document.getElementById('loanTermUnit').value;
    
    if (startDate && loanTerm) {
        const start = new Date(startDate);
        let end = new Date(start);
        
        if (loanTermUnit === 'months') {
            end.setMonth(end.getMonth() + loanTerm);
        } else if (loanTermUnit === 'years') {
            end.setFullYear(end.getFullYear() + loanTerm);
        }
        
        // Subtract 1 day for proper loan term boundaries
        end.setDate(end.getDate() - 1);
        
        document.getElementById('endDate').value = end.toISOString().split('T')[0];
    }
}
```

#### Reverse Calculation (Start Date + End Date → Loan Term)
```javascript
function recalculateLoanTerm() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    
    if (startDate && endDate) {
        const start = new Date(startDate);
        const end = new Date(endDate);
        const diffTime = Math.abs(end - start);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        const loanTermUnit = document.getElementById('loanTermUnit').value;
        let loanTerm;
        
        if (loanTermUnit === 'months') {
            loanTerm = Math.round(diffDays / 30.44); // Average days per month
        } else if (loanTermUnit === 'years') {
            loanTerm = Math.round(diffDays / 365.25); // Average days per year
        }
        
        document.getElementById('loanTerm').value = loanTerm;
    }
}
```

### Event Listeners for Date Synchronization
**File**: `templates/calculator.html` (Lines 1227-1230)
```javascript
document.getElementById('startDate').addEventListener('change', calculateEndDate);
document.getElementById('loanTerm').addEventListener('input', calculateEndDate);
document.getElementById('endDate').addEventListener('click', makeEndDateEditable);
document.getElementById('endDate').addEventListener('change', recalculateLoanTerm);
```

### Modifying Date Behavior

#### To Change Default Date Logic:
1. **File**: `templates/calculator.html`
2. **Function**: `setDefaultDate()` (Line 1220)
3. **Modification**: Change `const today = new Date().toISOString().split('T')[0];`

#### To Modify Date Calculation:
1. **Forward Calculation**: Modify `calculateEndDate()` function (Line 1090)
2. **Reverse Calculation**: Modify `recalculateLoanTerm()` function (Line 1145)
3. **Date Difference Logic**: Modify days-to-months conversion factors

#### To Add Custom Date Validation:
```javascript
function validateDateRange() {
    const startDate = new Date(document.getElementById('startDate').value);
    const endDate = new Date(document.getElementById('endDate').value);
    
    // Add custom validation logic here
    if (endDate <= startDate) {
        alert('End date must be after start date');
        return false;
    }
    
    // Add minimum/maximum term limits
    const diffDays = Math.abs(endDate - startDate) / (1000 * 60 * 60 * 24);
    if (diffDays < 30) {
        alert('Minimum loan term is 30 days');
        return false;
    }
    
    return true;
}
```

---

## 3. Complete Field Lineage Documentation

### Field Data Flow Architecture

```
Frontend Form Field → JavaScript Collection → API Request → Backend Processing → Calculation Engine → Response → Frontend Display
```

### Comprehensive Field Mapping

#### A. Basic Loan Information
| Field Name | HTML ID | Form Name | JS Variable | Backend Parameter | Calculation Variable | Display Location |
|------------|---------|-----------|-------------|-------------------|---------------------|------------------|
| Loan Name | `loanName` | `loanName` | `formData.loanName` | `data.get('loanName')` | Not used | Summary header |
| Loan Type | `loanType` | `loan_type` | `formData.loan_type` | `data.get('loan_type')` | `loan_type` | Summary type badge |
| Repayment Option | `repaymentOption` | `repayment_option` | `formData.repayment_option` | `data.get('repayment_option')` | `repayment_option` | Payment schedule |
| Currency | `currency` | `currency` | `formData.currency` | `data.get('currency')` | `currency` | All currency symbols |

#### B. Financial Fields
| Field Name | HTML ID | Form Name | JS Variable | Backend Parameter | Calculation Variable | Display Location |
|------------|---------|-----------|-------------|-------------------|---------------------|------------------|
| Property Value | `propertyValue` | `property_value` | `formData.property_value` | `float(data.get('property_value'))` | `property_value` | Summary table, LTV calculation |
| Gross Amount | `grossAmountFixed` | `gross_amount` | `formData.gross_amount` | `float(data.get('gross_amount'))` | `gross_amount` | Primary calculation input |
| Net Amount | `netAmountInput` | `net_amount` | `formData.net_amount` | `float(data.get('net_amount'))` | `net_amount` | Net-to-gross conversion |
| Interest Rate | `annualRate` | `interest_rate` | `formData.interest_rate` | `float(data.get('interest_rate'))` | `interest_rate` | Interest calculations |
| Loan Term | `loanTerm` | `loan_term` | `formData.loan_term` | `int(data.get('loan_term'))` | `loan_term` | Payment schedule |

#### C. Date Fields
| Field Name | HTML ID | Form Name | JS Variable | Backend Parameter | Calculation Variable | Display Location |
|------------|---------|-----------|-------------|-------------------|---------------------|------------------|
| Start Date | `startDate` | `start_date` | `formData.start_date` | `data.get('start_date')` | `start_date` | Schedule start, LTV calculation |
| End Date | `endDate` | `end_date` | `formData.end_date` | `data.get('end_date')` | `end_date` | Schedule end, term calculation |
| Loan Term Unit | `loanTermUnit` | `loan_term_unit` | `formData.loan_term_unit` | `data.get('loan_term_unit')` | `loan_term_unit` | Date calculations |

#### D. Fee Fields
| Field Name | HTML ID | Form Name | JS Variable | Backend Parameter | Calculation Variable | Display Location |
|------------|---------|-----------|-------------|-------------------|---------------------|------------------|
| Arrangement Fee Rate | `arrangementFeeRate` | `arrangement_fee_rate` | `formData.arrangement_fee_rate` | `float(data.get('arrangement_fee_rate'))` | `arrangement_fee_rate` | Fee calculation |
| Legal Costs | `legalCosts` | `legal_costs` | `formData.legal_costs` | `float(data.get('legal_costs'))` | `legal_costs` | Net advance calculation |
| Site Visit Fee | `siteVisitFee` | `site_visit_fee` | `formData.site_visit_fee` | `float(data.get('site_visit_fee'))` | `site_visit_fee` | Fee breakdown |
| Title Insurance Rate | `titleInsuranceRate` | `title_insurance_rate` | `formData.title_insurance_rate` | `float(data.get('title_insurance_rate'))` | `title_insurance_rate` | Insurance calculation |

### Field Validation Chain

#### Frontend Validation (JavaScript)
**File**: `static/js/calculator.js` (Lines 2700+)
```javascript
validateFormData(formData) {
    const errors = [];
    
    // Required field validation
    if (!formData.loanName || formData.loanName.trim() === '') {
        errors.push('Loan name is required');
    }
    
    // Numeric validation
    if (formData.gross_amount <= 0 && formData.net_amount <= 0) {
        errors.push('Either gross amount or net amount must be greater than 0');
    }
    
    // Date validation
    if (formData.start_date && formData.end_date) {
        const start = new Date(formData.start_date);
        const end = new Date(formData.end_date);
        if (end <= start) {
            errors.push('End date must be after start date');
        }
    }
    
    return errors;
}
```

#### Backend Validation (Python)
**File**: `routes.py` (Lines 140+)
```python
def validate_loan_parameters(data):
    """Validate incoming loan parameters"""
    errors = []
    
    # Required fields
    if not data.get('loan_type'):
        errors.append('Loan type is required')
    
    # Numeric validation
    gross_amount = float(data.get('gross_amount', 0) or 0)
    net_amount = float(data.get('net_amount', 0) or 0)
    
    if gross_amount <= 0 and net_amount <= 0:
        errors.append('Either gross amount or net amount must be provided')
    
    # Interest rate validation
    interest_rate = float(data.get('interest_rate', 0) or 0)
    if interest_rate <= 0 or interest_rate > 50:
        errors.append('Interest rate must be between 0 and 50%')
    
    return errors
```

---

## 4. Loan Type & Repayment Calculation Logic

### Calculation Engine Location
**File**: `simple_calculator.py`

### Bridge Loan Calculations

#### A. Bridge Loan - Retained Interest (repayment_option: 'none')
**Location**: `simple_calculator.py` (Lines 10-55)
```python
def calculate_bridge_loan(self, params: Dict) -> Dict:
    gross_amount = float(params.get('gross_amount', 0) or 0)
    interest_rate = float(params.get('interest_rate', 12) or 12)
    loan_term = int(params.get('loan_term', 12) or 12)
    
    # Total interest calculation (retained at start)
    total_interest = gross_amount * (interest_rate / 100) * (loan_term / 12)
    
    # Fee calculations
    arrangement_fee = gross_amount * 0.02  # 2% of gross
    legal_costs = 2000  # Fixed amount
    site_visit_fee = 500  # Fixed amount
    title_insurance = property_value * 0.0001  # 0.01% of property value
    
    # Net advance (amount available to borrower)
    net_advance = gross_amount - arrangement_fee - legal_costs - site_visit_fee - title_insurance - total_interest
    
    return result_dictionary
```

**To Modify Bridge Loan Calculation:**
1. **File**: `simple_calculator.py`
2. **Function**: `calculate_bridge_loan()` (Line 10)
3. **Interest Formula**: Line 30 - `total_interest = amount * (interest_rate / 100) * (loan_term / 12)`
4. **Fee Rates**: Lines 33-36 - Modify percentage rates and fixed amounts
5. **Net Advance Formula**: Line 39 - Modify deduction logic

#### B. Bridge Loan - Service Only (repayment_option: 'service_only')
**Enhanced Calculation Location**: Future implementation in `calculations.py`
```python
def calculate_bridge_service_only(self, params):
    # Monthly interest payments, no principal reduction
    monthly_interest = (gross_amount * interest_rate / 100) / 12
    total_interest = monthly_interest * loan_term
    net_advance = gross_amount - fees_only  # No interest deduction
```

### Term Loan Calculations

#### A. Term Loan - Amortizing (repayment_option: 'service_and_capital')
**Location**: `simple_calculator.py` (Lines 65-67)
```python
def calculate_term_loan(self, params: Dict) -> Dict:
    # Currently uses same logic as bridge loan
    # TODO: Implement proper amortizing calculation
    return self.calculate_bridge_loan(params)
```

**To Implement Proper Term Loan Calculation:**
```python
def calculate_term_loan_amortizing(self, params):
    gross_amount = float(params.get('gross_amount', 0))
    interest_rate = float(params.get('interest_rate', 12)) / 100 / 12  # Monthly rate
    loan_term_months = int(params.get('loan_term', 12))
    
    # Monthly payment calculation (PMT formula)
    if interest_rate > 0:
        monthly_payment = gross_amount * (interest_rate * (1 + interest_rate)**loan_term_months) / ((1 + interest_rate)**loan_term_months - 1)
    else:
        monthly_payment = gross_amount / loan_term_months
    
    total_payments = monthly_payment * loan_term_months
    total_interest = total_payments - gross_amount
    
    return {
        'monthlyPayment': monthly_payment,
        'totalInterest': total_interest,
        'totalPayments': total_payments
    }
```

### Development Loan Calculations

#### A. Development Loan - Basic (loan_type: 'development')
**Location**: `simple_calculator.py` (Lines 69-75)
```python
def calculate_development_loan(self, params: Dict) -> Dict:
    result = self.calculate_bridge_loan(params)
    # Development loans typically have compound interest
    if result.get('success'):
        result['totalInterest'] *= 1.2  # 20% more for development complexity
    return result
```

#### B. Development Loan - Excel Goal Seek (loan_type: 'development2')
**Enhanced Location**: Future implementation
```python
def calculate_development_excel_goal_seek(self, params):
    net_amount = float(params.get('net_amount', 0))
    interest_rate = float(params.get('interest_rate', 14)) / 100
    loan_term_days = int(params.get('loan_term_days', 546))
    
    # Iterative goal seek to find gross amount
    def goal_seek_function(gross_amount):
        # Compound daily interest calculation
        daily_rate = interest_rate / 365
        compound_factor = (1 + daily_rate) ** loan_term_days
        calculated_net = gross_amount / compound_factor - fees
        return abs(calculated_net - net_amount)
    
    # Use numerical optimization to find gross amount
    from scipy.optimize import minimize_scalar
    result = minimize_scalar(goal_seek_function, bounds=(net_amount, net_amount * 2))
    optimal_gross = result.x
    
    return {
        'grossAmount': optimal_gross,
        'netAmount': net_amount,
        'goalSeekAccuracy': result.fun
    }
```

### Repayment Option Logic
**File**: `static/js/calculator.js` (Lines 1300+)

#### Dynamic Repayment Options Based on Loan Type
```javascript
updateRepaymentOptions() {
    const loanType = document.getElementById('loanType').value;
    const repaymentSelect = document.getElementById('repaymentOption');
    
    // Clear existing options
    repaymentSelect.innerHTML = '';
    
    let options = [];
    
    if (loanType === 'bridge') {
        options = [
            { value: 'none', text: 'Retained Interest (Interest Only)' },
            { value: 'service_only', text: 'Service Only (Interest Payments)' },
            { value: 'service_and_capital', text: 'Service + Capital (Principal & Interest)' },
            { value: 'flexible_payment', text: 'Flexible Payment Schedule' }
        ];
    } else if (loanType === 'term') {
        options = [
            { value: 'service_only', text: 'Interest Only Payments' },
            { value: 'service_and_capital', text: 'Amortizing (Principal & Interest)' }
        ];
    } else if (loanType === 'development' || loanType === 'development2') {
        options = [
            { value: 'none', text: 'Retained Interest (Roll-up)' },
            { value: 'service_only', text: 'Interest Only Payments' },
            { value: 'service_and_capital', text: 'Interest + Principal Payments' }
        ];
    }
    
    // Populate dropdown
    options.forEach(option => {
        const optionElement = document.createElement('option');
        optionElement.value = option.value;
        optionElement.textContent = option.text;
        repaymentSelect.appendChild(optionElement);
    });
}
```

**To Modify Repayment Options:**
1. **File**: `static/js/calculator.js`
2. **Function**: `updateRepaymentOptions()` (Line 1300+)
3. **Add New Option**: Add to appropriate loan type array
4. **Backend Handler**: Add case in calculation engine

---

## 5. Output Modification Guide

### Summary Table Output
**File**: `templates/calculator.html` (Lines 1000-1070)

#### Summary Table Structure
```html
<table class="table table-striped" id="summaryTable">
    <tbody>
        <tr><td>Gross Amount</td><td id="grossAmountResult">-</td></tr>
        <tr><td>Net Advance</td><td id="netAdvanceResult">-</td></tr>
        <tr><td>Total Interest</td><td id="totalInterestResult">-</td></tr>
        <tr><td>Arrangement Fee</td><td id="arrangementFeeResult">-</td></tr>
        <tr><td>Legal Costs</td><td id="legalCostsResult">-</td></tr>
        <tr><td>Site Visit Fee</td><td id="siteVisitFeeResult">-</td></tr>
        <tr><td>Title Insurance</td><td id="titleInsuranceResult">-</td></tr>
        <tr><td>Property Valuation</td><td id="propertyValueResult">-</td></tr>
        <tr><td>Monthly Payment</td><td id="monthlyPaymentResult">-</td></tr>
        <tr><td>Start LTV</td><td id="startLTVResult">-</td></tr>
        <tr><td>End LTV</td><td id="endLTVResult">-</td></tr>
    </tbody>
</table>
```

#### JavaScript Display Update Function
**File**: `static/js/calculator.js` (Lines 2800+)
```javascript
displayResults(result) {
    const currency = document.getElementById('currency').value;
    const symbol = currency === 'EUR' ? '€' : '£';
    
    // Update summary table
    document.getElementById('grossAmountResult').textContent = 
        symbol + result.grossAmount.toLocaleString('en-GB', {minimumFractionDigits: 2});
    document.getElementById('netAdvanceResult').textContent = 
        symbol + result.netAdvance.toLocaleString('en-GB', {minimumFractionDigits: 2});
    document.getElementById('totalInterestResult').textContent = 
        symbol + result.totalInterest.toLocaleString('en-GB', {minimumFractionDigits: 2});
    // ... additional field updates
}
```

#### To Add New Summary Fields:

1. **Add HTML Row** (`templates/calculator.html`):
```html
<tr><td>New Field Name</td><td id="newFieldResult">-</td></tr>
```

2. **Add Backend Calculation** (`simple_calculator.py`):
```python
result['newField'] = calculated_value
```

3. **Add JavaScript Display** (`static/js/calculator.js`):
```javascript
document.getElementById('newFieldResult').textContent = 
    symbol + result.newField.toLocaleString('en-GB', {minimumFractionDigits: 2});
```

### Detailed Payment Schedule
**File**: `static/js/calculator.js` (Lines 3000+)

#### Payment Schedule Generation
```javascript
generatePaymentSchedule(result) {
    const scheduleTable = document.getElementById('paymentScheduleTable');
    const tbody = scheduleTable.querySelector('tbody');
    tbody.innerHTML = ''; // Clear existing rows
    
    // Generate schedule based on loan type and repayment option
    const paymentSchedule = result.paymentSchedule || [];
    
    paymentSchedule.forEach((payment, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${payment.date}</td>
            <td>${formatCurrency(payment.openingBalance)}</td>
            <td>${formatCurrency(payment.interestPayment)}</td>
            <td>${formatCurrency(payment.principalPayment)}</td>
            <td>${formatCurrency(payment.totalPayment)}</td>
            <td>${formatCurrency(payment.closingBalance)}</td>
        `;
        tbody.appendChild(row);
    });
}
```

#### To Modify Payment Schedule Columns:

1. **Update HTML Header** (`templates/calculator.html`):
```html
<th>New Column Name</th>
```

2. **Update JavaScript Generation** (`static/js/calculator.js`):
```javascript
<td>${formatCurrency(payment.newColumnValue)}</td>
```

3. **Update Backend Schedule** (`simple_calculator.py`):
```python
schedule_entry = {
    'date': payment_date,
    'openingBalance': opening_balance,
    'newColumnValue': calculated_value,
    # ... other fields
}
```

### Chart Modifications
**File**: `static/js/calculator.js` (Lines 3500+)

#### Chart Configuration
```javascript
generateCharts(result) {
    // Payment Schedule Chart
    const paymentChartCtx = document.getElementById('paymentChart').getContext('2d');
    const paymentChart = new Chart(paymentChartCtx, {
        type: 'line',
        data: {
            labels: result.paymentSchedule.map(p => p.date),
            datasets: [{
                label: 'Outstanding Balance',
                data: result.paymentSchedule.map(p => p.closingBalance),
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Loan Balance Over Time'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '£' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}
```

#### To Add New Charts:

1. **Add HTML Canvas** (`templates/calculator.html`):
```html
<canvas id="newChart" width="400" height="200"></canvas>
```

2. **Add JavaScript Chart Generation** (`static/js/calculator.js`):
```javascript
const newChartCtx = document.getElementById('newChart').getContext('2d');
const newChart = new Chart(newChartCtx, {
    type: 'bar', // or 'line', 'pie', 'doughnut'
    data: {
        labels: result.labels,
        datasets: [{
            label: 'New Chart Data',
            data: result.chartData,
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 1
        }]
    },
    options: {
        // Chart configuration options
    }
});
```

---

## 6. Advanced Customization

### Adding New Loan Types

#### Step 1: Frontend Dropdown Option
**File**: `templates/calculator.html` (Line 448)
```html
<option value="new_loan_type">New Loan Type</option>
```

#### Step 2: JavaScript Handler
**File**: `static/js/calculator.js` (Line 1300+)
```javascript
} else if (loanType === 'new_loan_type') {
    options = [
        { value: 'new_repayment', text: 'New Repayment Option' }
    ];
}
```

#### Step 3: Backend Calculation
**File**: `simple_calculator.py`
```python
def calculate_new_loan_type(self, params: Dict) -> Dict:
    # Implement new loan calculation logic
    return {
        'success': True,
        'grossAmount': calculated_gross,
        'netAdvance': calculated_net,
        # ... other fields
    }
```

#### Step 4: Route Handler
**File**: `routes.py` (Line 160+)
```python
elif loan_type == 'new_loan_type':
    result = calculator.calculate_new_loan_type(data)
```

### Custom Field Validation

#### Client-Side Validation
**File**: `static/js/calculator.js`
```javascript
addCustomValidation() {
    document.getElementById('customField').addEventListener('blur', function() {
        const value = parseFloat(this.value);
        if (value < 0 || value > 1000000) {
            this.classList.add('is-invalid');
            // Show error message
        } else {
            this.classList.remove('is-invalid');
        }
    });
}
```

#### Server-Side Validation
**File**: `routes.py`
```python
def validate_custom_field(value):
    try:
        numeric_value = float(value)
        if numeric_value < 0 or numeric_value > 1000000:
            return "Value must be between 0 and 1,000,000"
    except ValueError:
        return "Invalid numeric value"
    return None
```

### Currency Support Extension

#### Add New Currency
**File**: `templates/calculator.html` (Line 470)
```html
<option value="USD">USD ($)</option>
```

#### Update Currency Symbols
**File**: `static/js/calculator.js` (Line 2000+)
```javascript
updateCurrencySymbols() {
    const currency = document.getElementById('currency').value;
    let symbol;
    
    switch(currency) {
        case 'EUR': symbol = '€'; break;
        case 'USD': symbol = '$'; break;
        default: symbol = '£'; break;
    }
    
    document.querySelectorAll('.currency-symbol').forEach(el => {
        el.textContent = symbol;
    });
}
```

### Performance Optimization

#### Debounced Calculations
```javascript
class CalculationDebouncer {
    constructor(delay = 500) {
        this.delay = delay;
        this.timeoutId = null;
    }
    
    debounce(func) {
        clearTimeout(this.timeoutId);
        this.timeoutId = setTimeout(func, this.delay);
    }
}

// Usage
const debouncer = new CalculationDebouncer(300);
document.getElementById('grossAmountFixed').addEventListener('input', () => {
    debouncer.debounce(() => {
        // Perform calculation
    });
});
```

#### Caching Results
```javascript
class ResultsCache {
    constructor(maxSize = 50) {
        this.cache = new Map();
        this.maxSize = maxSize;
    }
    
    getCacheKey(formData) {
        return JSON.stringify(formData);
    }
    
    get(formData) {
        const key = this.getCacheKey(formData);
        return this.cache.get(key);
    }
    
    set(formData, result) {
        const key = this.getCacheKey(formData);
        
        if (this.cache.size >= this.maxSize) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }
        
        this.cache.set(key, result);
    }
}
```

---

## File Modification Quick Reference

### Critical Files and Their Purposes
- **`templates/calculator.html`**: Frontend form structure and JavaScript
- **`static/js/calculator.js`**: Client-side calculation logic and UI management
- **`routes.py`**: API endpoints and request handling
- **`simple_calculator.py`**: Core calculation engine
- **`replit.md`**: Project documentation and architecture notes

### Common Modification Patterns
1. **New Input Field**: HTML → JavaScript collection → Backend parameter → Calculation usage
2. **New Output Field**: Calculation result → JavaScript display → HTML table row
3. **New Validation**: Frontend JavaScript → Backend Python → Error handling
4. **New Chart**: Data preparation → Chart.js configuration → HTML canvas

### Testing Your Modifications
1. **Frontend Changes**: Browser developer console for JavaScript errors
2. **Backend Changes**: Check Replit console for Python errors
3. **API Testing**: Use browser network tab or curl commands
4. **Full Integration**: Test complete calculation flow

This guide provides comprehensive coverage of the loan calculator system architecture and modification procedures. Each section includes specific file locations, line numbers, and code examples for efficient development.