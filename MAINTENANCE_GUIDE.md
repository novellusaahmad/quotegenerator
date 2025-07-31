# Novellus Loan Management - Maintenance & Cleanup Guide

## Project Structure (After Cleanup)

### Core Application Files
```
├── app.py                          # Flask application setup
├── main.py                         # Application entry point  
├── routes.py                       # API routes and request handling
├── calculations.py                 # Core loan calculation logic
├── models.py                       # Database models
├── auth.py                         # Authentication helpers
└── utils.py                        # Utility functions
```

### Document Generators
```
├── professional_quote_generator.py # Professional Word document generator
└── excel_generator.py             # Excel spreadsheet generator
```

### Templates & Static Files
```
├── templates/
│   ├── base.html                   # Base template
│   ├── calculator.html             # Main calculator interface
│   ├── index.html                  # Homepage
│   └── [other UI templates]
└── static/
    ├── css/                        # Stylesheets
    ├── js/calculator.js            # Calculator JavaScript logic
    ├── favicon.ico                 # Site favicon
    └── novellus_logo.png           # Company logo
```

### Configuration & Documentation  
```
├── replit.md                       # Project documentation & preferences
├── LOAN_CALCULATION_GUIDE.md       # Technical calculation guide
├── MAINTENANCE_GUIDE.md            # This maintenance guide
├── SYSTEM_DOCUMENTATION.md         # System overview
├── README.md                       # Setup instructions
├── pyproject.toml                  # Python dependencies
└── requirements.txt                # Deployment requirements
```

### Installation Scripts
```
├── install.sh                      # Unix/Linux installer
├── install.bat                     # Windows installer  
├── install_windows.bat             # Windows-specific installer
├── start.sh                        # Unix/Linux startup
├── start.bat                       # Windows startup
└── start_windows.bat               # Windows-specific startup
```

## Files Removed During Cleanup

### Test Files (Removed)
- `test_*.py` - Various calculation test scripts
- `test_*.json` - Test response data
- `test_*.docx` - Test document outputs
- `test_*.xlsx` - Test Excel files
- `test_*.pdf` - Test PDF outputs

### Backup Files (Removed)
- `pdf_quote_generator_backup.py`
- `pdf_quote_generator_simple.py`
- `current_response.json`
- `different_date_response.json`
- Various other backup JSON files

### Development Artifacts (Removed)
- `attached_assets/` - Screenshots and development files (80+ files)
- `find_exact_rate.py` - Rate calculation utility
- `loan_calculator.py` - Duplicate calculator class
- `quote_generator.py` - Old quote generator
- `aylesbury_quote_generator.py` - Specific template generator
- `chart_generator.py` - Chart generation utility
- `database_init.py` - Database initialization script
- `weasyprint_error.log` - Error log files

## Maintenance Procedures

### 1. Regular Cleanup Tasks

#### Monthly Cleanup
```bash
# Remove temporary files
find . -name "*.log" -delete
find . -name "*.tmp" -delete
find . -name "*~" -delete

# Clean Python cache
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

# Clean development artifacts
rm -f test_*.* debug_*.* temp_*.*
```

#### Database Maintenance
```bash
# Check database size
du -h novellus_loans.db

# Backup database
cp novellus_loans.db backup_$(date +%Y%m%d).db

# Clean old sessions (if using database sessions)
# Add to scheduled task
```

### 2. Code Maintenance

#### Adding New Features
1. **Update Core Logic** (`calculations.py`)
   - Add new calculation methods
   - Ensure Decimal precision
   - Add comprehensive logging

2. **Update API Routes** (`routes.py`)
   - Add new endpoints
   - Update field mapping
   - Add validation

3. **Update Frontend** (`templates/calculator.html`, `static/js/calculator.js`)
   - Add UI controls
   - Update form handling
   - Test responsiveness

4. **Update Generators** (`professional_quote_generator.py`, `excel_generator.py`)
   - Add new document sections
   - Update field mapping
   - Test export functionality

#### Code Quality Checks
```bash
# Check for unused imports
python -c "import ast; print('Check manually for unused imports')"

# Validate Python syntax
python -m py_compile *.py

# Check for common issues
grep -r "TODO\|FIXME\|XXX" *.py
```

### 3. Dependency Management

#### Updating Dependencies
```bash
# Check current versions
pip list

# Update specific packages
pip install --upgrade flask sqlalchemy

# Update requirements
pip freeze > requirements.txt
```

#### Security Updates
- Monitor for security advisories
- Update critical packages promptly
- Test thoroughly after updates

### 4. Performance Monitoring

#### Key Metrics to Monitor
- **Calculation Speed**: Log calculation times
- **Memory Usage**: Monitor during complex calculations
- **Database Performance**: Query execution times
- **File Generation**: PDF/Excel generation times

#### Performance Optimization
```python
# Add timing to critical functions
import time
start_time = time.time()
# ... calculation logic ...
print(f"Calculation took {time.time() - start_time:.3f}s")
```

### 5. Backup Procedures

#### Critical Data to Backup
1. **Database**: `novellus_loans.db`
2. **Configuration**: `.env`, `pyproject.toml`
3. **Templates**: `templates/` directory
4. **Static Assets**: `static/` directory
5. **Documentation**: `*.md` files

#### Backup Script
```bash
#!/bin/bash
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir $BACKUP_DIR

# Copy critical files
cp novellus_loans.db $BACKUP_DIR/
cp -r templates/ $BACKUP_DIR/
cp -r static/ $BACKUP_DIR/
cp *.md $BACKUP_DIR/
cp pyproject.toml $BACKUP_DIR/

# Compress
tar -czf ${BACKUP_DIR}.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

echo "Backup created: ${BACKUP_DIR}.tar.gz"
```

### 6. Troubleshooting Common Issues

#### Issue: Calculation Results Incorrect
**Diagnosis Steps:**
1. Check logs for calculation method being used
2. Verify input parameter extraction in `routes.py`
3. Test with known reference values
4. Check for Decimal/float type mixing

**Common Fixes:**
- Ensure consistent Decimal usage
- Verify field mapping between frontend/backend
- Check date handling and loan_term_days

#### Issue: Export Generation Fails
**Diagnosis Steps:**
1. Test with minimal data set
2. Check field mapping in generator
3. Verify calculation result structure
4. Test template file access

**Common Fixes:**
- Update field mapping in generators
- Check file permissions
- Verify template file paths

#### Issue: Frontend Not Updating
**Diagnosis Steps:**
1. Check browser console for JavaScript errors
2. Verify API response structure
3. Test field mapping
4. Check currency symbol replacement

**Common Fixes:**
- Clear browser cache
- Update field mapping in JavaScript
- Fix API response structure

### 7. Development Best Practices

#### Code Standards
- Use Decimal for all financial calculations
- Add comprehensive logging for debugging
- Maintain consistent field naming
- Document complex calculation logic

#### Testing Approach
- Test all loan types with reference values
- Verify calculations against Excel
- Test all repayment options
- Test document generation

#### Documentation Updates
- Update `replit.md` for architectural changes
- Update `LOAN_CALCULATION_GUIDE.md` for calculation changes
- Document any new configuration options
- Update installation instructions if needed

### 8. Production Deployment

#### Pre-deployment Checklist
- [ ] All calculations tested and verified
- [ ] All document exports working
- [ ] Database migrations completed
- [ ] Environment variables configured
- [ ] Backup procedures in place
- [ ] Monitoring configured

#### Deployment Steps
1. Backup current version
2. Update code repository
3. Install/update dependencies
4. Run database migrations
5. Restart application server
6. Verify functionality
7. Monitor for issues

This maintenance guide ensures the Novellus Loan Management System remains stable, performant, and easy to maintain while supporting future enhancements and bug fixes.