# Novellus Loan Management System

A clean, focused loan calculation and management system with advanced financial computations, professional document generation, and PostgreSQL database persistence. Simplified architecture for reliable on-premise deployment.

## 🚀 Quick Start

### Automated Installation & Launch

**Linux/macOS:**
```bash
./install.sh
```

**Windows:**
```cmd
install.bat
```

The installation script will:
- ✅ Install Python dependencies and virtual environment
- ✅ Install and configure PostgreSQL database
- ✅ Create required directories (uploads, reports_output, etc.)
- ✅ Configure environment variables
- ✅ Initialize database with all required tables
- ✅ Run system tests

### Starting the Application

**Linux/macOS:**
```bash
./start.sh
```

**Windows:**
```cmd
start.bat
```

The start script will:
- ✅ Check database and initialize if needed
- ✅ Create required directories
- ✅ Start with the best available server (Gunicorn/Waitress/Python)
- ✅ Open application at `http://localhost:5000`

## 📋 System Requirements

- **Python**: 3.8+ (automatically checked during installation)
- **Operating System**: Windows 10+, macOS 10.14+, Ubuntu 18.04+, CentOS 7+
- **Memory**: 512MB RAM minimum, 1GB recommended
- **Disk Space**: 200MB for installation + database storage

## ⚡ Features

### 🧮 Advanced Loan Calculations
- **Bridge Loans**: Retained interest, service-only, service+capital, flexible payments
- **Term Loans**: Interest-only, amortizing payments with precise scheduling
- **Development Loans**: Compound daily interest with tranche management
- **Development 2 Loans**: Advanced Excel Goal Seek methodology with perfect accuracy
- **Multi-Currency**: GBP and EUR support with proper formatting
- **Date Sensitivity**: Calculations respond to actual calendar days
- **Precision Mathematics**: Decimal-based calculations for financial accuracy

### 📄 Professional Document Generation
- **Word Documents**: Professional loan quotes with Novellus branding
- **Excel Spreadsheets**: Detailed payment schedules and breakdowns
- **PDF Reports**: Alternative PDF generation options
- **Template System**: Customizable document templates

### 💾 Database Management
- **PostgreSQL Database**: Production-ready database with SSL support
- **Optional Snowflake Sync**: Configure Snowflake and push data in real time
- **Loan History**: Complete storage of all calculations and parameters
- **Version Control**: Automatic versioning of loan modifications
- **Search & Filter**: Advanced search capabilities across loan history
- **CRUD Operations**: Create, view, edit, and delete loan records
- **Data Export**: Generate quotes from historical calculations

### ☁️ Cloud Deployment
- **Azure Container Apps**: Production-ready containerized deployment
- **Auto-scaling**: Automatic scaling based on demand
- **CI/CD Pipeline**: GitHub Actions for automated deployments
- **Database Integration**: Azure PostgreSQL with SSL encryption
- **Monitoring**: Application Insights and Log Analytics integration

## 🚀 Azure Deployment

### Quick Azure Deployment

**Prerequisites:**
- Azure subscription with Container Apps and PostgreSQL permissions
- Azure CLI installed and configured
- Docker installed locally

**Automated Deployment:**
```bash
# Run the automated deployment script
./azure-deploy-script.sh
```

The script will:
- ✅ Create Azure Resource Group and Container Registry
- ✅ Set up PostgreSQL database with SSL encryption
- ✅ Build and push Docker image to Azure Container Registry
- ✅ Deploy Container App with auto-scaling configuration
- ✅ Configure all environment variables and secrets
- ✅ Provide application URL for immediate access

**Manual Deployment:**
See [AZURE_DEPLOYMENT_GUIDE.md](AZURE_DEPLOYMENT_GUIDE.md) for detailed step-by-step instructions.

### Azure Resources Created
- **Container App**: Auto-scaling web application (1-3 replicas)
- **Container Registry**: Private Docker image repository
- **PostgreSQL**: Flexible server with SSL encryption
- **Container Apps Environment**: Managed container hosting environment
- **Application Insights**: Monitoring and analytics (optional)

### Deployment Features
- **Zero-downtime deployments** with rolling updates
- **Automatic SSL/TLS** certificates for custom domains
- **Health checks** and automatic restart on failure
- **Log aggregation** with Azure Monitor
- **Secrets management** with Azure Container Apps secrets
- **CI/CD integration** with GitHub Actions

### Cost Optimization
- **Consumption-based pricing** - pay only for actual usage
- **Auto-scaling** to zero during low usage periods
- **Burstable database tier** for cost-effective development
- **Resource limits** to prevent unexpected charges

### 🎨 User Interface
- **Modern Design**: Bootstrap 5 with Novellus gold/navy color scheme
- **Responsive Layout**: Works on desktop, tablet, and mobile devices
- **Interactive Charts**: Chart.js visualizations for payment schedules
- **Notifications**: Professional toast notification system
- **Theme Support**: Multiple UI themes including Document theme

## 🔧 Technical Architecture

### Backend Stack
- **Framework**: Flask 3.0+ with SQLAlchemy ORM
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Authentication**: Flask-Login with JWT token support
- **File Processing**: python-docx, mammoth, openpyxl, ReportLab
- **Server Options**: Gunicorn (Linux/macOS), Waitress (Windows), Python dev server

### Frontend Stack
- **CSS Framework**: Bootstrap 5.3+
- **JavaScript**: Vanilla JS with Chart.js for visualizations
- **Icons**: Font Awesome 6
- **Charts**: Chart.js for payment schedule visualization
- **Notifications**: Custom toast notification system

### Key Files
- `main.py` - Application entry point
- `app.py` - Flask application factory and configuration
- `models.py` - Database models and relationships
- `calculations.py` - Core loan calculation engine
- `routes.py` - API endpoints and web routes
- `professional_quote_generator.py` - Document generation
- `excel_generator.py` - Excel export functionality

## 🛠 Development Setup

### Manual Installation (Advanced)

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd novellus-loan-system
   ```

2. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate.bat # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r deploy_requirements.txt
   ```

4. **Initialize Database**
   ```bash
   python database_init.py
   ```

5. **Start Application**
   ```bash
   gunicorn --bind 0.0.0.0:5000 --reload main:app
   ```

### Environment Configuration

The `.env` file is automatically created with default values:

```env
SESSION_SECRET=novellus-loan-management-secret-key-2025
DATABASE_URL=sqlite:///novellus_loans.db
FLASK_ENV=development
FLASK_DEBUG=True
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```

## 📊 Usage Examples

### Basic Loan Calculation
1. Navigate to `http://localhost:5000`
2. Select loan type (Bridge/Term/Development)
3. Enter loan parameters (amount, rate, term)
4. Click "Calculate" to see results
5. Save loan to history for future reference

### Generate Professional Quotes
1. Go to "History" page
2. Find saved loan calculation
3. Click download dropdown
4. Select "Professional Quote" or "Excel Quote"
5. Document downloads automatically

### Advanced Features
- **Payment Scheduling**: View detailed month-by-month payment breakdowns
- **Interest Analysis**: See compound daily vs. simple interest comparisons  
- **Fee Management**: Handle arrangement fees, legal costs, title insurance
- **Tranche Management**: Support for development loan tranche releases

## 🔍 Troubleshooting

### Common Issues

**"Database initialization failed"**
- Solution: Run `python database_init.py` manually
- Check Python path and virtual environment activation

**"WeasyPrint installation failed" (Windows)**
- This is normal - ReportLab is used as fallback for PDF generation
- All functionality remains available

**"Gunicorn not found"**
- Normal on Windows - Waitress or Python dev server used instead
- Application functionality unchanged

**"Permission denied" (Linux/macOS)**
- Run `chmod +x install.sh start.sh` to make scripts executable

### Log Files
- Application logs: `logs/` directory (created automatically)
- Installation logs: Console output during installation
- Database logs: Included in application logs

## 🚀 Deployment

### Production Deployment
1. Run installation script on target server
2. Configure production database in `.env`:
   ```env
   DATABASE_URL=postgresql://user:pass@localhost/dbname
   FLASK_ENV=production
   FLASK_DEBUG=False
   ```
3. Start with production server:
   ```bash
   gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
   ```

### Docker Deployment (Optional)
The system can be containerized using the provided Python dependencies and SQLite database for simple deployment scenarios.

## 📚 Documentation

- **System Documentation**: `SYSTEM_DOCUMENTATION.md`
- **Calculation Guide**: `LOAN_CALCULATION_GUIDE.md`  
- **Maintenance Guide**: `MAINTENANCE_GUIDE.md`
- **Deployment Guide**: `DEPLOYMENT_GUIDE.md`
- **Windows Guide**: `README_WINDOWS.md`

## 🔒 Security Features

- **Input Validation**: Comprehensive form validation and sanitization
- **File Upload Security**: Type checking and secure file handling
- **Authentication**: Session management with CSRF protection
- **Database Security**: Parameterized queries and ORM protection
- **Environment Variables**: Secure configuration management

## 📈 Performance

- **Database Optimization**: Connection pooling and query optimization
- **Calculation Caching**: Efficient financial computation caching
- **File Processing**: Optimized document generation
- **Server Options**: Production-ready server configurations

## 🧊 Snowflake Integration

The application stores data in PostgreSQL by default. To optionally sync data to Snowflake:

1. Configure the connection:
   ```http
   POST /api/snowflake/config
   {
     "user": "<username>",
     "password": "<password>",
     "account": "<account>",
     "warehouse": "<warehouse>",
     "database": "<database>",
     "schema": "<schema>"
   }
   ```
2. Sync records in real time:
   ```http
   POST /api/snowflake/sync
   {
     "table": "target_table",
     "data": {"column": "value"}
   }
   ```

## 🆘 Support

For technical support or feature requests:
1. Check troubleshooting section above
2. Review system documentation files
3. Ensure all dependencies are properly installed
4. Verify database initialization completed successfully

The system includes comprehensive logging and error handling to help diagnose any issues.
