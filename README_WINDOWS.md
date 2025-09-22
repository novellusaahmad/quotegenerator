# Windows Installation - Quick Start Guide

## For Windows Users Experiencing WeasyPrint Issues

If you're seeing this error during installation:
```
WeasyPrint could not import some external libraries
cannot load library 'libgobject-2.0-0': error 0x7e
```

**This is normal on Windows!** The application will work perfectly without WeasyPrint.

## Solution 1: Use Windows-Optimized Installer (Recommended)

1. Download all project files to a folder (e.g., `C:\LoanMaster\`)
2. Open Command Prompt as Administrator
3. Navigate to the folder: `cd C:\LoanMaster\`
4. Run the Windows installer: `install_windows.bat`

This installer:
- ✅ Skips problematic WeasyPrint installation
- ✅ Uses ReportLab for reliable PDF generation
- ✅ Installs all required dependencies
- ✅ Tests everything works correctly

## Solution 2: Manual Installation

If you prefer manual control:

```cmd
# Create virtual environment
python -m venv venv
venv\Scripts\activate.bat

# Install core dependencies
pip install flask flask-sqlalchemy flask-login flask-cors
pip install reportlab matplotlib pandas numpy
pip install python-docx openpyxl xlsxwriter
pip install waitress python-dateutil

# Skip WeasyPrint - not needed for Windows
# Initialize database
python database_init.py

# Start application
python main.py
```

## Available Features (Without WeasyPrint)

- ✅ **PDF Generation**: Professional quotes using ReportLab
- ✅ **Excel Export**: Full spreadsheets with charts
- ✅ **Loan Calculations**: Bridge, Term, Development loans
- ✅ **Payment Schedules**: Detailed analysis and charts
- ✅ **Web Interface**: Complete loan management system

## Starting the Application

After installation, choose one of these methods:

**Method 1 (Recommended for Windows):**
1. Run: `start_windows.bat`
2. Open browser to: http://localhost:5000

**Method 2 (General):**
1. Run: `start.bat`
2. Open browser to: http://localhost:5000

**Method 3 (Manual):**
```cmd
venv\Scripts\activate.bat
waitress-serve --host=0.0.0.0 --port=5000 main:app
```

## Why WeasyPrint and Gunicorn Fail on Windows

**WeasyPrint Issues:**
WeasyPrint requires GTK libraries (libgobject-2.0, libpango, libcairo) that are:
- Difficult to install on Windows
- Not available through pip
- Require manual system-level installation

**Gunicorn Issues:**
Gunicorn uses the `fcntl` module which is Unix-only and not available on Windows.

**Solutions:**
- **PDF Generation**: ReportLab (reliable Windows alternative)
- **Web Server**: Waitress (Windows-compatible WSGI server)

## Need Help?

1. Try the Windows-optimized installer: `install_windows.bat`
2. Check the full guide: `WINDOWS_INSTALLATION_GUIDE.md`
3. Verify Python 3.8+ is installed with PATH enabled
4. Run Command Prompt as Administrator

The application will work perfectly for all loan management tasks without WeasyPrint.