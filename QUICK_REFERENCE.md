# Novellus Loan System - Quick Reference Guide

## Most Common Modifications

### 🎨 Visual Changes (Colors, Layout, Styling)

**File**: `static/css/novellus-theme.css`

**Change Colors**:
```css
:root {
    --novellus-gold: #B8860B;    /* Primary brand color */
    --novellus-navy: #1E2B3A;    /* Secondary brand color */
}
```

**Modify Result Cards**:
- Search for `.result-card` sections
- Update gradients, hover effects, text colors

**Adjust Table Layouts**:
- Search for `.schedule-table` and `#calculationBreakdownTable`
- Modify column widths, font sizes, padding

---

### 💰 Calculation Changes

**File**: `calculations.py`

**Add New Fee Type**:
1. Find `_calculate_fees()` method
2. Add new fee calculation
3. Update form in `calculator.html`
4. Update PDF/Excel generators

**Modify Interest Calculations**:
1. Find `calculate_interest_amount()` method
2. Update formula for specific interest type
3. Test with known values

**Add New Repayment Option**:
1. Add to `calculate_bridge_loan()` or `calculate_term_loan()`
2. Create new `_calculate_*_*()` method
3. Update payment schedule generation

---

### 📊 Chart Modifications

**File**: `static/js/calculator.js`

**Change Chart Colors**:
```javascript
// Find updateChart() function
backgroundColor: '#B8860B',  // Novellus gold
borderColor: '#1E2B3A',      // Novellus navy
```

**Add New Chart Type**:
1. Add canvas element to `calculator.html`
2. Create new chart initialization in JavaScript
3. Process data in `updateChart()` function

---

### 📝 Form Changes

**Files**: `templates/calculator.html` + `static/js/calculator.js`

**Add New Input Field**:
1. **HTML**: Add form field in calculator.html
2. **JavaScript**: Update form data collection
3. **Backend**: Add parameter to routes.py
4. **Calculation**: Use parameter in calculations.py

**Change Field Options**:
- Find select dropdown in HTML
- Add/remove option elements
- Update JavaScript validation if needed

---

### 📄 Document Generation

**PDF Changes** (`pdf_quote_generator.py`):
- Colors: Update `NOVELLUS_GOLD` and `NOVELLUS_NAVY` constants
- Layout: Modify `_add_header()` and `_add_footer()` methods
- Content: Add sections in `generate_quote_pdf()`

**Excel Changes** (`excel_generator.py`):
- Styling: Update `_create_styles()` method
- Content: Modify sheet generation methods
- New Sheets: Add worksheet creation in main method

---

## File Structure Quick Reference

```
├── calculations.py          # 🧮 All loan calculations
├── routes.py               # 🌐 Web endpoints and request handling
├── static/css/novellus-theme.css  # 🎨 Styling and colors
├── static/js/calculator.js  # ⚡ Frontend behavior and charts
├── templates/calculator.html # 📱 Main calculator interface
├── pdf_quote_generator.py   # 📄 PDF document generation
├── excel_generator.py      # 📊 Excel export functionality
├── models.py               # 🗄️ Database schema
├── auth.py                 # 🔐 User authentication
└── app.py                  # ⚙️ Flask application setup
```

---

## Emergency Fixes

### Tables Show Horizontal Scrolling
**File**: `static/css/novellus-theme.css`
- Find table CSS sections
- Add `table-layout: fixed; width: 100%;`
- Adjust column width percentages

### Calculations Return Zero
**File**: `calculations.py`
- Check Decimal vs float type mixing
- Add debug logging to find the issue
- Verify all parameters are properly converted

### Charts Not Displaying
**File**: `static/js/calculator.js`
- Check browser console for JavaScript errors
- Verify Chart.js library is loaded
- Test with minimal data first

### Form Validation Failing
**Files**: `calculator.html` + `calculator.js`
- Check form field names match JavaScript
- Verify validation rules in `validateForm()`
- Test with simple inputs first

---

## Testing Checklist

### After Calculation Changes:
- [ ] Test all loan types (bridge, term, development)
- [ ] Test all repayment options
- [ ] Verify payment schedules generate correctly
- [ ] Check PDF and Excel exports work

### After Visual Changes:
- [ ] Test on desktop, tablet, and mobile
- [ ] Verify tables don't show horizontal scrolling
- [ ] Check color contrast for accessibility
- [ ] Test all interactive elements

### After Form Changes:
- [ ] Test form validation with various inputs
- [ ] Verify all fields submit correctly
- [ ] Check dynamic field show/hide logic
- [ ] Test error message display

---

## Common Patterns

### Adding New Loan Type:
1. Add calculation method in `calculations.py`
2. Add form option in `calculator.html`
3. Update JavaScript in `calculator.js`
4. Add route handling in `routes.py`
5. Update document generators

### Changing Novellus Branding:
1. Update CSS variables in `novellus-theme.css`
2. Update PDF colors in `pdf_quote_generator.py`
3. Update Excel colors in `excel_generator.py`
4. Test all components for consistency

### Database Changes:
1. Update model in `models.py`
2. Create and run migration
3. Update forms if user input required
4. Update validation rules