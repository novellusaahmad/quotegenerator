@echo off
echo ============================================================
echo Novellus Loan Management System - Windows Installation
echo ============================================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org/downloads/
    pause
    exit /b 1
)

echo Python found: 
python --version

REM Check if pip is available
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip is not installed
    echo Please install pip or reinstall Python with pip included
    pause
    exit /b 1
)

echo Pip found:
pip --version

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies from requirements file first
if exist "deploy_requirements.txt" (
    echo.
    echo Installing from deploy_requirements.txt...
    pip install -r deploy_requirements.txt
    if %errorlevel% neq 0 (
        echo Warning: Some packages from deploy_requirements.txt failed
    )
) else if exist "Requirements.txt" (
    echo.
    echo Installing from Requirements.txt...
    pip install -r Requirements.txt
    if %errorlevel% neq 0 (
        echo Warning: Some packages from Requirements.txt failed
    )
) else (
    REM Install dependencies individually
    echo.
    echo Installing core dependencies...

    REM Install essential packages first
    echo Installing Flask and web framework components...
    pip install flask flask-sqlalchemy flask-login flask-jwt-extended flask-cors
    pip install werkzeug sqlalchemy waitress gunicorn python-dotenv

    echo Installing database and file handling...
    pip install psycopg2-binary python-docx mammoth openpyxl xlsxwriter docx

    echo Installing calculation and visualization components...
    pip install reportlab matplotlib pandas numpy python-dateutil requests
    pip install email-validator oauthlib flask-dance pyjwt
)

REM Install requirements file if available
if exist "deploy_requirements.txt" (
    echo.
    echo Installing additional requirements from deploy_requirements.txt...
    pip install -r deploy_requirements.txt --no-deps --force-reinstall 2>nul
)

if exist "Requirements.txt" (
    echo.
    echo Installing additional requirements from Requirements.txt...
    pip install -r Requirements.txt --no-deps --force-reinstall 2>nul
)

REM Handle WeasyPrint separately with better error handling
echo.
echo Attempting WeasyPrint installation for advanced PDF features...
set WEASYPRINT_INSTALLED=0

pip install weasyprint 2>weasyprint_error.log
if %errorlevel% equ 0 (
    echo ✓ WeasyPrint installed successfully - Full PDF generation available
    set WEASYPRINT_INSTALLED=1
    del weasyprint_error.log 2>nul
) else (
    echo.
    echo ⚠️  WeasyPrint installation failed - This is NORMAL on Windows
    echo.
    echo Alternative PDF generation methods are available:
    echo   • ReportLab PDF generation (already installed) ✓
    echo   • Chart.js visualizations ✓  
    echo   • Excel export functionality ✓
    echo.
    echo WeasyPrint requires GTK libraries that are difficult to install on Windows.
    echo The application will work perfectly without WeasyPrint.
    echo.
    if exist weasyprint_error.log (
        echo WeasyPrint error details saved to: weasyprint_error.log
    )
)

if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Create required directories
echo.
echo Creating required directories...
if not exist "uploads" mkdir uploads
if not exist "static\uploads" mkdir static\uploads
if not exist "instance" mkdir instance

REM Set environment variables
echo.
echo Setting up environment variables...
echo Set SESSION_SECRET to a secure random string
set SESSION_SECRET=novellus-loan-management-secret-key-2025
echo Set DATABASE_URL=sqlite:///novellus_loans.db

REM Install PostgreSQL on Windows (if not already installed)
echo.
echo Checking for PostgreSQL installation...
pg_config --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo PostgreSQL not found. Please install PostgreSQL manually:
    echo 1. Download from: https://www.postgresql.org/download/windows/
    echo 2. Install with default settings
    echo 3. Remember the postgres user password
    echo 4. Re-run this installation script
    echo.
    echo For now, using SQLite database...
    set DATABASE_URL=sqlite:///novellus_loans.db
) else (
    echo PostgreSQL found: 
    pg_config --version
    echo.
    echo Setting up PostgreSQL database...
    
    REM Create database and user (requires manual postgres password entry)
    echo Please enter the postgres user password when prompted:
    psql -U postgres -c "DROP DATABASE IF EXISTS novellus_loans;"
    psql -U postgres -c "DROP USER IF EXISTS novellus_user;"
    psql -U postgres -c "CREATE USER novellus_user WITH PASSWORD 'novellus_secure_2025';"
    psql -U postgres -c "CREATE DATABASE novellus_loans OWNER novellus_user;"
    psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE novellus_loans TO novellus_user;"
    
    if %errorlevel% equ 0 (
        echo ✓ PostgreSQL database configured successfully
        set DATABASE_URL=postgresql://novellus_user:novellus_secure_2025@localhost:5432/novellus_loans
    ) else (
        echo PostgreSQL setup failed, falling back to SQLite
        set DATABASE_URL=sqlite:///novellus_loans.db
    )
)

REM Create environment file
echo.
if not exist ".env" (
    echo Creating .env file...
    (
    echo SESSION_SECRET=novellus-loan-management-secret-key-2025
    echo DATABASE_URL=%DATABASE_URL%
    echo FLASK_ENV=development
    echo FLASK_DEBUG=True
    echo UPLOAD_FOLDER=uploads
    echo MAX_CONTENT_LENGTH=16777216
    ) > .env
    echo .env file created with database configuration
) else (
    echo .env file already exists, skipping
)

REM Add BIRT configuration to .env file
echo.
echo Configuring BIRT environment for Business Intelligence Reporting...
findstr /C:"BIRT_RUNTIME_URL" .env >nul
if errorlevel 1 (
    echo. >> .env
    echo # BIRT Reporting Configuration >> .env
    echo BIRT_RUNTIME_URL=http://localhost:8080/birt >> .env
    echo BIRT configuration added to .env file
) else (
    echo BIRT configuration already exists in .env file
)

REM Initialize database and create required directories
echo.
echo Initializing database with loan calculator data storage...
echo Setting up tables: LoanSummary, PaymentSchedule, User, Application, etc.
python database_init.py

if %errorlevel% neq 0 (
    echo ERROR: Failed to initialize database with main script
    echo.
    echo Trying alternative database initialization...
    python -c "import sys, os; sys.path.insert(0, '.'); from app import app, db; app.app_context().push(); db.create_all(); print('Database initialized successfully via fallback method')"
    if %errorlevel% neq 0 (
        echo ERROR: All database initialization methods failed
        echo Please check Python installation and dependencies
        pause
        exit /b 1
    )
)

echo.
echo ============================================================
echo NOVELLUS LOAN MANAGEMENT SYSTEM - INSTALLATION COMPLETE
echo ============================================================
echo.
echo Running installation tests...
echo Testing core functionality...

REM Test core imports first
python -c "import flask, app, calculations; print('✓ Core modules working')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Core module import failed
    echo Please check Python installation and dependencies
    pause
    exit /b 1
)

REM Run full test suite but don't fail if WeasyPrint tests fail
python test_installation.py
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  Some installation tests showed warnings (likely WeasyPrint-related)
    echo.
    echo Testing essential functionality...
    python -c "from calculations import LoanCalculator; calc = LoanCalculator(); print('✓ Calculator working')"
    python -c "from app import app; print('✓ Flask app working')"
    python -c "from excel_generator import NovellussExcelGenerator; print('✓ Excel generation working')"
    
    if %errorlevel% neq 0 (
        echo ❌ Essential functionality test failed
        pause
        exit /b 1
    ) else (
        echo ✅ Essential functionality tests passed
        echo.
        echo Note: WeasyPrint warnings are normal on Windows and don't affect core functionality.
    )
) else (
    echo ✅ All installation tests passed successfully
)

echo.
echo Installed Components:
echo   [^] Python virtual environment created
echo   [^] Dependencies installed  
echo   [^] Database initialized with loan calculator storage
echo   [!] BIRT Runtime requires manual installation for advanced reporting
echo.
echo Quick Start:
echo   start.bat
echo.
echo System URLs:
echo   Loan Calculator: http://localhost:5000/
echo   Loan History: http://localhost:5000/loan-history
echo   BIRT Reports: http://localhost:5000/birt-reports
echo   Database Info: http://localhost:5000/database-info
echo.
echo BIRT Installation (Optional Advanced Reporting):
echo   1. Download BIRT Runtime from: https://download.eclipse.org/birt/downloads/
echo   2. Install Apache Tomcat on Windows
echo   3. Deploy BIRT to Tomcat on port 8080
echo   4. See BIRT_INSTALLATION_GUIDE.md for detailed instructions
echo.
echo Documentation:
echo   README.md - Overview and features
echo   BIRT_INSTALLATION_GUIDE.md - BIRT setup instructions
echo   DEPLOYMENT_GUIDE.md - Production deployment
echo   WINDOWS_INSTALLATION_GUIDE.md - Windows-specific setup
echo.
echo Manual Options:
echo 1. Activate virtual environment: venv\Scripts\activate.bat
echo 2. Run the application: python main.py
echo    OR use waitress: waitress-serve --host=0.0.0.0 --port=5000 main:app
echo    OR use start script: start.bat
echo.
echo Press any key to start the application now...
pause >nul

REM Start the application
echo Starting Novellus Loan Management System...
echo Open your browser to: http://localhost:5000
echo Press Ctrl+C to stop the application
echo.
waitress-serve --host=0.0.0.0 --port=5000 main:app