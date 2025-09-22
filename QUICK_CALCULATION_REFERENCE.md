# Quick Calculation Reference Card

## 🎯 Most Commonly Modified Calculations

### 🔴 **Interest Rate Formulas**

#### Standard Interest Calculation (Bridge/Term)
```python
# Location: calculations.py:85-120, 485-520
interest = (gross_amount * interest_rate * loan_term_days) / (365 * 100)
```

#### Development Loan Compound Daily Interest
```python
# Location: calculations.py:885-950
daily_rate = interest_rate / 100 / 365
compound_interest = principal * (((1 + daily_rate) ** days) - 1)
```

### 🟡 **Net Advance Formulas**

#### Interest Retained (Bridge/Term)
```python
# Location: calculations.py:85-120, 485-520
net_advance = gross_amount - arrangement_fee - legal_fees - site_visit_fee - title_insurance - total_interest
```

#### Service Only/Service+Capital (Bridge/Term)
```python
# Location: calculations.py:125-160, 525-560
net_advance = gross_amount - arrangement_fee - legal_fees - site_visit_fee - title_insurance
# Note: Interest NOT deducted for these repayment types
```

#### Development Loans
```python
# Location: calculations.py:750-800
net_advance = gross_amount - arrangement_fee - legal_fees - site_visit_fee - title_insurance - total_interest
```

### 🟢 **Net-to-Gross Conversion Formulas**

#### Bridge/Term Interest Retained
```python
# Location: calculations.py:335-420, 725-810
gross = (net + legal_fees) / (1 - arrangement_fee_rate - title_insurance_rate - (interest_rate * months/12)/100)
```

#### Bridge/Term Service Only/Service+Capital
```python
# Location: calculations.py:335-420, 725-810
gross = (net + legal_fees) / (1 - arrangement_fee_rate - title_insurance_rate)
```

#### Development Goal Seek
```python
# Location: calculations.py:805-880
gross = (net + all_fees + compound_daily_interest) / 0.98
```

### 🔵 **Fee Calculations**

#### Arrangement Fee
```python
# Location: Throughout calculations.py
arrangement_fee = gross_amount * (arrangement_fee_percentage / 100)
```

#### Title Insurance
```python
# Location: Throughout calculations.py
title_insurance = gross_amount * (title_insurance_rate / 100)
```

### 🟠 **Payment Schedule Key Functions**

#### Bridge Payment Schedule
```python
# Location: calculations.py:1455-1580
def _generate_detailed_bridge_schedule(repayment_option, ...)
```

#### Term Payment Schedule  
```python
# Location: calculations.py:1585-1710
def _generate_detailed_term_schedule(repayment_option, ...)
```

#### Development Payment Schedule
```python
# Location: calculations.py:1715-1840
def _generate_development_schedule(...)
```

## 🔧 **Quick Modification Checklist**

### Before Making Changes:
- [ ] Identify the loan type and repayment option
- [ ] Locate the specific calculation function
- [ ] Check if change affects payment schedule generation
- [ ] Note if change impacts export functions

### After Making Changes:
- [ ] Test with known working examples
- [ ] Verify all repayment types for that loan type
- [ ] Check Excel/DOCX exports still work
- [ ] Test both gross-to-net and net-to-gross calculations

## 🎨 **Color Code Legend**

- 🔴 **High Risk**: Core interest/net advance calculations
- 🟡 **Medium Risk**: Fee calculations and payment schedules  
- 🟢 **Low Risk**: Display formatting and validation
- 🔵 **Special**: Development loan Goal Seek algorithm
- 🟠 **Export**: Excel/DOCX generation functions

## 📍 **Emergency Fixes - Common Issues**

### Interest Calculation Wrong
**File**: `calculations.py`  
**Functions**: `_calculate_[loan_type]_[repayment_type]()`  
**Line Range**: 85-330 (bridge), 485-720 (term), 885-950 (development)

### Net Advance Incorrect
**File**: `calculations.py`  
**Search**: `net_advance =` or `netAdvance`  
**Check**: Ensure correct fees are deducted based on repayment type

### Payment Schedule Missing/Wrong
**File**: `calculations.py`  
**Functions**: `_generate_detailed_[loan_type]_schedule()`  
**Line Range**: 1455-1840

### Export Not Working
**Files**: `excel_generator.py`, `professional_quote_generator.py`  
**Check**: Field mapping functions in `routes.py`

## 🚀 **Performance Tips**

- Use global search for function names across files
- Comment old code instead of deleting during testing
- Keep backup copies of working formulas
- Test with simple values first (£1M, 12%, 12 months)

---

*Keep this reference handy when making quick calculation modifications!*