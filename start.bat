@echo off
echo ============================================================
echo Starting Novellus Loan Management System
echo ============================================================

REM Start BIRT Runtime if available
echo Starting BIRT Runtime for advanced reporting...
set BIRT_STATUS=Not available

REM Check if BIRT setup exists
if exist "birt_setup" (
    echo Found BIRT setup directory, starting Tomcat...
    cd birt_setup
    
    if exist "start_birt.sh" (
        echo Starting BIRT via start_birt.sh...
        start /b bash start_birt.sh
        timeout /t 10 /nobreak >nul
        
        REM Check if BIRT is accessible
        curl -s "http://localhost:8080/birt/" >nul 2>&1
        if !errorlevel! equ 0 (
            echo [SUCCESS] BIRT Runtime started successfully
            set BIRT_STATUS=Available at http://localhost:8080/birt/
        ) else (
            echo [WARNING] BIRT Runtime started but not accessible yet
            set BIRT_STATUS=Starting (may take a moment)
        )
    ) else (
        echo [WARNING] BIRT startup script not found
    )
    
    cd ..
) else (
    echo [WARNING] BIRT Runtime not found - advanced reporting features will be limited
    echo           Run install.bat to install BIRT or see BIRT_INSTALLATION_GUIDE.md
)

echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found
    echo Please run install.bat first to set up the application
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found, creating default configuration...
    (
    echo SESSION_SECRET=novellus-loan-management-secret-key-2025
    echo DATABASE_URL=sqlite:///novellus_loans.db
    echo FLASK_ENV=development
    echo FLASK_DEBUG=True
    echo UPLOAD_FOLDER=uploads
    echo MAX_CONTENT_LENGTH=16777216
    echo.
    echo # BIRT Reporting Configuration
    echo BIRT_RUNTIME_URL=http://localhost:8080/birt
    ) > .env
    echo .env file created with BIRT configuration
) else (
    REM Add BIRT configuration if missing
    findstr /C:"BIRT_RUNTIME_URL" .env >nul
    if errorlevel 1 (
        echo. >> .env
        echo # BIRT Reporting Configuration >> .env
        echo BIRT_RUNTIME_URL=http://localhost:8080/birt >> .env
        echo BIRT configuration added to .env file
    )
)

REM Ensure database is initialized
echo Checking database and loan calculator storage...
if not exist "novellus_loans.db" (
    if not exist "instance\novellus_loans.db" (
        echo Initializing database...
        python database_init.py
        if %errorlevel% neq 0 (
            echo ERROR: Database initialization failed, trying fallback...
            python -c "import sys, os; sys.path.insert(0, '.'); from app import app, db; app.app_context().push(); db.create_all(); print('Database initialized successfully')"
            if %errorlevel% neq 0 (
                echo ERROR: All database initialization methods failed
                pause
                exit /b 1
            )
        )
    ) else (
        echo Database found in instance folder
    )
) else (
    echo Database found in root folder
)

REM Ensure required directories exist
echo Creating required directories...
if not exist "uploads" mkdir uploads
if not exist "static\uploads" mkdir static\uploads
if not exist "instance" mkdir instance
if not exist "logs" mkdir logs

REM Start the application
echo.
echo ============================================================
echo NOVELLUS LOAN MANAGEMENT SYSTEM - STARTING
echo ============================================================
echo.
echo System Status:
echo   [^] Database: Initialized and ready
echo   [^] Python Environment: Active
if "%BIRT_STATUS%"=="Available" (
    echo   [^] BIRT Runtime: Available
) else (
    echo   [!] BIRT Runtime: Not accessible
)
echo.
echo Application URLs:
echo   Loan Calculator: http://localhost:5000/
echo   Loan History: http://localhost:5000/loan-history
echo   BIRT Reports: http://localhost:5000/birt-reports
echo   Database Info: http://localhost:5000/database-info
if "%BIRT_STATUS%"=="Available" (
    echo   BIRT Runtime: http://localhost:8080/birt/frameset
)
echo.
echo Press Ctrl+C to stop the application
echo ============================================================
echo.

REM Try servers in order of preference: Waitress (best for Windows), Gunicorn, Python dev server
echo Attempting to start with best available server...

echo Trying Waitress (recommended for Windows)...
waitress-serve --host=0.0.0.0 --port=5000 main:app 2>nul
if %errorlevel% neq 0 (
    echo Waitress not available, trying Gunicorn...
    gunicorn --bind 0.0.0.0:5000 --reload main:app 2>nul
    if %errorlevel% neq 0 (
        echo Gunicorn not found, using Python development server...
        python main.py
    )
)

echo.
echo Application stopped.
pause