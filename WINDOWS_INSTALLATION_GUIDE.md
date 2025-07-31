# Novellus Loan Management System - Windows Installation Guide

## Quick Installation (Recommended)

1. **Download Project Files**
   - Extract all files to a folder (e.g., C:\LoanMaster\)

2. **Run Windows-Optimized Installation**
   - Open Command Prompt as Administrator
   - Navigate to project folder: `cd C:\LoanMaster\`
   - Run: `install_windows.bat` (Windows-optimized installer)
   - Or run: `install.bat` (general installer)
   - Wait for installation to complete

3. **Start Application**
   - Run: `start.bat`
   - Open browser to: http://localhost:5000

## Detailed Windows Setup

### Prerequisites

1. **Python 3.8+ Installation**
   - Download from: https://python.org/downloads/
   - During installation, check "Add Python to PATH"
   - Verify: Open cmd and run `python --version`

2. **Microsoft Visual C++ Build Tools** (Optional)
   - Usually installed automatically with Python
   - If needed: https://visualstudio.microsoft.com/visual-cpp-build-tools/

### Installation Process

The `install.bat` script automatically:
- Verifies Python installation
- Creates virtual environment in `venv` folder
- Installs all required Python packages
- Handles WeasyPrint installation (may show warnings - this is normal)
- Creates database and required directories
- Sets up environment configuration
- Runs installation tests

### Common Windows Issues and Solutions

#### Issue: "WeasyPrint could not import some external libraries"
**Status**: Normal warning on Windows - Cannot find libgobject-2.0-0
**Solution**: WeasyPrint is optional. PDF generation uses ReportLab instead.
**Details**: WeasyPrint requires GTK libraries (libgobject, libpango, etc.) that are difficult to install on Windows.

**Windows-Specific Solutions**:
1. **Use install_windows.bat** - Skips WeasyPrint, uses ReportLab (recommended)
2. **For WeasyPrint (advanced)**: 
   - Install GTK from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
   - Then: `pip install weasyprint`
3. **Alternative**: Application works perfectly with ReportLab PDF generation

#### Issue: "The process cannot access the file" during tests
**Status**: Normal Windows file locking behavior
**Solution**: Ignore this warning - functionality works correctly

#### Issue: "Python is not recognized"
**Solution**: 
1. Reinstall Python with "Add to PATH" checked
2. Or manually add Python to PATH environment variable

#### Issue: "pip is not recognized"
**Solution**: 
1. Python installation should include pip
2. Try: `python -m pip --version`

#### Issue: Permission errors
**Solution**: 
1. Run Command Prompt as Administrator
2. Ensure antivirus isn't blocking file creation

### Manual Installation (if automated fails)

```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate.bat

# Install dependencies
pip install -r Requirements.txt

# Initialize database
python database_init.py

# Test installation
python test_installation.py
```

### File Structure After Installation

```
LoanMaster\
├── venv\                 # Virtual environment (created during install)
├── uploads\              # File upload directory
├── static\               # CSS, JavaScript, images
├── templates\            # HTML templates
├── app.py               # Main application
├── install.bat          # Windows installation script
├── start.bat            # Windows startup script
├── .env                 # Environment configuration (created during install)
└── novellus_loans.db    # SQLite database (created during install)
```

### Starting the Application

#### Method 1: Using start.bat
```cmd
start.bat
```

#### Method 2: Manual startup
```cmd
# Activate virtual environment
venv\Scripts\activate.bat

# Start application
gunicorn --bind 0.0.0.0:5000 --reload main:app
```

#### Method 3: Python direct
```cmd
# Activate virtual environment
venv\Scripts\activate.bat

# Run with Python
python main.py
```

### Windows-Specific Features

1. **Automatic File Associations**
   - PDF downloads open in default PDF viewer
   - Excel files open in Excel or compatible application

2. **Windows Security**
   - Windows Defender may scan downloaded files
   - Antivirus software may flag Python executable creation

3. **File Path Considerations**
   - Avoid spaces and special characters in installation path
   - Use short paths if possible (e.g., C:\LoanMaster\ not C:\Program Files\Long Folder Name\)

### Performance Optimization for Windows

1. **Disable Windows Search Indexing** for project folder
2. **Add Python to Windows Defender exclusions**
3. **Use SSD storage** for better database performance
4. **Increase virtual memory** if working with large loan portfolios

### Troubleshooting Tools

#### Check Installation Status
```cmd
python test_installation.py
```

#### Verify Python Environment
```cmd
python --version
pip list
```

#### Test Core Components
```cmd
python -c "from calculations import LoanCalculator; print('Calculator OK')"
python -c "from pdf_quote_generator import generate_quote_pdf; print('PDF OK')"
```

#### Check Database
```cmd
python -c "from app import db; print('Database OK')"
```

### Support Resources

1. **Python Documentation**: https://docs.python.org/
2. **Flask Documentation**: https://flask.palletsprojects.com/
3. **Windows Command Line**: https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/

### Uninstallation

To remove the application:
1. Delete the entire project folder
2. Python and system packages remain for other applications

### Version Compatibility

- **Windows 10**: Fully supported
- **Windows 11**: Fully supported  
- **Windows 8.1**: Supported (Python 3.8+ required)
- **Windows Server**: Supported (2016+)

### Development Mode

For developers wanting to modify the application:
1. Install Git for Windows
2. Use Visual Studio Code or PyCharm
3. Enable Flask debug mode in `.env` file
4. Install additional development packages if needed

This guide ensures successful installation and operation of the Novellus Loan Management System on Windows platforms.