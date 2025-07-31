# Novellus Loan Management System - Installation Files

This directory contains all the files needed to install and deploy the Novellus Loan Management System on local machines.

## Installation Files

### Automated Installation Scripts

| File | Platform | Description |
|------|----------|-------------|
| `install.bat` | Windows | Automated installation script for Windows systems |
| `install.sh` | Linux/macOS | Automated installation script for Unix-based systems |
| `start.bat` | Windows | Quick start script for Windows |
| `start.sh` | Linux/macOS | Quick start script for Unix-based systems |

### Configuration Files

| File | Purpose |
|------|---------|
| `deploy_requirements.txt` | Python dependencies for deployment |
| `.env` | Environment configuration (created during installation) |

### Documentation

| File | Content |
|------|---------|
| `README.md` | Main application documentation |
| `DEPLOYMENT_GUIDE.md` | Detailed deployment instructions |
| `INSTALLATION_FILES.md` | This file - overview of installation files |

### Testing

| File | Purpose |
|------|---------|
| `test_installation.py` | Installation validation script |

## Quick Start Guide

### For Windows Users

1. **Download** all files to your desired directory
2. **Run**: Double-click `install.bat`
3. **Start**: Double-click `start.bat`

### For Linux/macOS Users

1. **Download** all files to your desired directory
2. **Run**: `chmod +x *.sh && ./install.sh`
3. **Start**: `./start.sh`

## What Each Script Does

### install.bat / install.sh

- Checks Python installation and version
- Creates virtual environment
- Installs all required dependencies
- Creates necessary directories
- Sets up environment configuration
- Initializes database
- Runs installation tests
- Provides startup instructions

### start.bat / start.sh

- Activates virtual environment
- Checks configuration
- Starts the Gunicorn server
- Opens application on localhost:5000

### test_installation.py

- Validates Python version compatibility
- Tests all dependency imports
- Checks database connectivity
- Verifies file permissions
- Tests application startup
- Provides diagnostic information

## System Requirements

### Minimum Requirements

- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **Memory**: 4GB RAM
- **Storage**: 2GB free space
- **Network**: Internet connection for initial setup

### Recommended Requirements

- **Python**: 3.10 or higher
- **Memory**: 8GB RAM
- **Storage**: SSD with 5GB free space
- **Browser**: Modern web browser (Chrome, Firefox, Safari, Edge)

## Dependencies

The system automatically installs these core dependencies:

### Web Framework
- Flask (web framework)
- Flask-SQLAlchemy (database ORM)
- Flask-Login (authentication)
- Flask-JWT-Extended (JWT tokens)
- Flask-CORS (cross-origin requests)

### Database
- SQLAlchemy (database toolkit)
- psycopg2-binary (PostgreSQL adapter)

### Document Processing
- python-docx (Word documents)
- openpyxl (Excel files)
- reportlab (PDF generation)
- weasyprint (PDF styling)

### Data Analysis
- pandas (data manipulation)
- numpy (numerical computing)
- matplotlib (charts and graphs)

### Utilities
- python-dateutil (date handling)
- email-validator (email validation)
- gunicorn (production server)

## Troubleshooting

### Common Issues

**Python not found:**
- Install Python from python.org
- Ensure Python is added to PATH

**Permission denied (Linux/macOS):**
- Run: `chmod +x install.sh start.sh`
- Use sudo for system package installation

**Virtual environment fails:**
- Install python3-venv: `sudo apt install python3-venv`

**Dependencies fail to install:**
- Install system development tools
- Check internet connection
- Update pip: `pip install --upgrade pip`

**Database connection error:**
- Check DATABASE_URL in .env file
- Ensure SQLite permissions
- Try running test_installation.py

**Port 5000 in use:**
- Change port in start scripts
- Kill existing processes: `pkill -f gunicorn`

### Getting Help

1. **Run the test script**: `python test_installation.py`
2. **Check logs**: Review console output for error messages
3. **Verify requirements**: Ensure system meets minimum requirements
4. **Manual installation**: Follow DEPLOYMENT_GUIDE.md for manual steps

## Security Notes

### Development vs Production

The installation scripts set up a development environment by default:
- Debug mode enabled
- SQLite database
- Development secret keys

For production deployment:
- Change SESSION_SECRET to a secure value
- Use production database (PostgreSQL)
- Set FLASK_ENV=production
- Configure HTTPS and proper security headers

### File Permissions

The scripts create these directories with appropriate permissions:
- `uploads/` - For user file uploads
- `static/uploads/` - For static file serving
- `instance/` - For Flask instance configuration

## Features Enabled

After successful installation, you'll have access to:

### Core Features
- ✅ Advanced loan calculations (Bridge, Term, Development)
- ✅ Multi-currency support (GBP, EUR)
- ✅ Payment scheduling with flexible timing
- ✅ Professional PDF and Excel report generation
- ✅ User authentication and role management
- ✅ Visual analytics with charts and graphs

### Professional Output
- ✅ Novellus-branded documents
- ✅ Detailed calculation breakdowns
- ✅ Payment schedules with formulas
- ✅ Chart visualizations
- ✅ Professional styling throughout

Your Novellus Loan Management System installation is now complete and ready for use!