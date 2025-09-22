# Deployment Verification Guide

## Quick Deployment Check

After installing the system, verify everything is working correctly:

### 1. Database Connection
```bash
python3 -c "from app import db; print('✓ Database connection successful')"
```

### 2. Application Startup
```bash
./start.sh
```
Expected output: Server starts at http://0.0.0.0:5000

### 3. Loan Calculator Test
- Navigate to the loan calculator interface
- Enter test values: £1,000,000 gross amount, 12% interest rate
- Click "Calculate" button
- Verify loan summary displays correctly

## Common Issues & Solutions

### SQLAlchemy URL Parsing Error
**Error:** `Could not parse SQLAlchemy URL from given URL string`

**Solution:** This indicates the DATABASE_URL environment variable is missing or malformed.

1. Check .env file exists with proper DATABASE_URL format:
   ```
   DATABASE_URL=postgresql://novellus_user:novellus_secure_2025@localhost/novellus_loans
   ```

2. Verify PostgreSQL service is running:
   ```bash
   sudo systemctl status postgresql
   sudo systemctl start postgresql  # if not running
   ```

3. Test database connection:
   ```bash
   python3 database_init.py
   ```

### SQLAlchemy Initialization Error
**Error:** Issues with SQLAlchemy(app, model_class=Base)

**Solution:** The app.py file uses modern SQLAlchemy 3.0+ initialization pattern:
```python
# Correct pattern
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Old pattern (causes errors)
db = SQLAlchemy(app, model_class=Base)
```

### Missing Dependencies
**Error:** ImportError for various Python packages

**Solution:** Reinstall dependencies with specific versions:
```bash
pip install "flask>=2.3.0" "flask-sqlalchemy>=3.0.0" "psycopg2-binary>=2.9.0"
```

## System Architecture

The simplified architecture includes:
- **Backend:** Flask + SQLAlchemy + PostgreSQL
- **Frontend:** Jinja2 templates + Bootstrap + vanilla JavaScript
- **Documents:** ReportLab (PDF) + python-docx (Word) + XlsxWriter (Excel)
- **Database:** PostgreSQL with SSL support

No Java, Tomcat, or BIRT dependencies required.

## Performance Verification

Expected system performance after deployment:
- **Database:** 25+ loan calculations stored
- **Response Time:** < 2 seconds for complex calculations
- **Memory Usage:** < 200MB for basic operations
- **File Generation:** PDF/Excel exports complete in < 5 seconds

## Clean Installation

For a completely fresh installation:

```bash
# Remove existing virtual environment
rm -rf venv

# Clean installation
./install.sh

# Start system
./start.sh
```

This ensures all dependencies are correctly installed with compatible versions.