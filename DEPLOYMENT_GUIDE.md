# Novellus Loan Management System - Deployment Guide

## Quick Installation

### Windows Users
1. Double-click `install.bat`
2. Follow the installation prompts
3. Use `start.bat` to run the application

### Linux/macOS Users
1. Run `./install.sh` in terminal
2. Use `./start.sh` to run the application

## Detailed Installation Steps

### 1. System Requirements

**Minimum Requirements:**
- Python 3.8 or higher
- 4GB RAM
- 2GB free disk space
- Internet connection for initial setup

**Recommended:**
- Python 3.10+
- 8GB RAM
- SSD storage
- Modern web browser (Chrome, Firefox, Safari, Edge)

### 2. Pre-Installation Setup

**Windows:**
- Install Python from [python.org](https://python.org/downloads/)
- Ensure "Add Python to PATH" is checked during installation
- Install Git for Windows (optional, for version control)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv
sudo apt-get install build-essential python3-dev libpq-dev
sudo apt-get install libffi-dev libssl-dev libxml2-dev libxslt1-dev
sudo apt-get install libjpeg-dev zlib1g-dev
```

**CentOS/RHEL:**
```bash
sudo yum update
sudo yum install python3 python3-pip python3-devel
sudo yum groupinstall 'Development Tools'
sudo yum install postgresql-devel libffi-devel openssl-devel
sudo yum install libxml2-devel libxslt-devel libjpeg-devel zlib-devel
```

**macOS:**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python3 postgresql libxml2 libxslt
```

### 3. Installation Process

#### Automatic Installation

**Windows:**
```cmd
install.bat
```

**Linux/macOS:**
```bash
chmod +x install.sh
./install.sh
```

#### Manual Installation

1. **Create Virtual Environment:**
   ```bash
   python3 -m venv venv
   ```

2. **Activate Virtual Environment:**
   ```bash
   # Linux/macOS
   source venv/bin/activate
   
   # Windows
   venv\Scripts\activate.bat
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r deploy_requirements.txt
   ```

4. **Create Environment File:**
   Create `.env` file with:
   ```
   SESSION_SECRET=your-very-secure-secret-key-here
   DATABASE_URL=sqlite:///novellus_loans.db
   FLASK_ENV=development
   FLASK_DEBUG=True
   ```

5. **Initialize Database:**
   ```bash
   python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database initialized')"
   ```

### 4. Starting the Application

#### Quick Start

**Windows:**
```cmd
start.bat
```

**Linux/macOS:**
```bash
./start.sh
```

#### Manual Start

1. **Activate Virtual Environment:**
   ```bash
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate.bat  # Windows
   ```

2. **Start Application:**
   ```bash
   gunicorn --bind 0.0.0.0:5000 --reload main:app
   ```

### 5. Accessing the Application

1. Open your web browser
2. Navigate to: `http://localhost:5000`
3. Register a new account or use existing credentials

### 6. Configuration Options

#### Database Configuration

**SQLite (Default):**
```
DATABASE_URL=sqlite:///novellus_loans.db
```

**PostgreSQL:**
```
DATABASE_URL=postgresql://username:password@localhost/novellus_loans
```

**MySQL:**
```
DATABASE_URL=mysql://username:password@localhost/novellus_loans
```

#### Production Settings

For production deployment, update `.env`:
```
SESSION_SECRET=your-production-secret-key
DATABASE_URL=your-production-database-url
FLASK_ENV=production
FLASK_DEBUG=False
```

### 7. Troubleshooting

#### Common Issues

**Issue: Python not found**
- Solution: Install Python and ensure it's in your PATH

**Issue: Permission denied (Linux/macOS)**
- Solution: Run `chmod +x install.sh start.sh`

**Issue: Virtual environment creation fails**
- Solution: Install python3-venv package

**Issue: Database connection error**
- Solution: Check DATABASE_URL in .env file

**Issue: Port 5000 already in use**
- Solution: Change port in start scripts or kill existing process

#### Dependency Issues

**If WeasyPrint fails to install:**
```bash
# Ubuntu/Debian
sudo apt-get install libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0

# macOS
brew install pango
```

**If psycopg2 fails to install:**
```bash
# Use binary version instead
pip install psycopg2-binary
```

### 8. Performance Optimization

#### For Better Performance

1. **Use Production Database:**
   - PostgreSQL recommended for production
   - Configure connection pooling

2. **Enable Caching:**
   - Add Redis for session storage
   - Implement application-level caching

3. **Production Server:**
   ```bash
   gunicorn --workers 4 --bind 0.0.0.0:5000 main:app
   ```

### 9. Security Considerations

#### Production Security

1. **Change Default Secret:**
   - Generate strong SESSION_SECRET
   - Use environment variables for secrets

2. **Database Security:**
   - Use strong database passwords
   - Enable SSL connections

3. **Web Server:**
   - Use HTTPS in production
   - Configure proper firewall rules

### 10. Backup and Maintenance

#### Database Backup

**SQLite:**
```bash
cp novellus_loans.db novellus_loans_backup_$(date +%Y%m%d).db
```

**PostgreSQL:**
```bash
pg_dump novellus_loans > backup_$(date +%Y%m%d).sql
```

#### Log Management

Logs are written to console by default. For production:
- Configure log rotation
- Monitor application logs
- Set up error alerting

### 11. Updates and Upgrades

#### Updating the Application

1. Stop the application
2. Backup your database
3. Update application files
4. Run database migrations if needed
5. Restart the application

### 12. Support

#### Getting Help

- Check the application logs for error messages
- Review this deployment guide
- Ensure all dependencies are properly installed
- Verify database connectivity

#### System Information

The application provides detailed logging to help diagnose issues:
- Check console output for error messages
- Review database initialization logs
- Monitor application startup sequence

## Features Available After Installation

- **Loan Calculator**: Advanced calculations for bridge, term, and development loans
- **Payment Scheduling**: Flexible timing and frequency options
- **Document Generation**: Professional PDF and Excel reports
- **User Management**: Registration and authentication system
- **Visual Analytics**: Charts and graphs for loan analysis
- **Multi-Currency**: GBP and EUR support

Your Novellus Loan Management System is now ready to use!