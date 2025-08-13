# Novellus Loan Management System – User Manual

*Version 2.1.0 | Last Updated: July 30, 2025*

---

## Table of Contents
1. [Introduction](#introduction)
2. [Landing Page and System Overview](#landing-page-and-system-overview)
3. [Loan Calculator Operations](#loan-calculator-operations)
4. [Loan History Management](#loan-history-management)
5. [Power BI Integration and Automation](#power-bi-integration-and-automation)
6. [System Administration](#system-administration)
7. [Net-to-Gross Calculation Formulas](#net-to-gross-calculation-formulas)
   1. [Bridge Loan Formulas](#bridge-loan-formulas)
   2. [Term Loan Formulas](#term-loan-formulas)
   3. [Development Loan Methodology](#development-loan-methodology)
8. [Calculation Logic Reference](#calculation-logic-reference)
9. [Installation and Deployment](#installation-and-deployment)
   1. [Quick Start Installation](#quick-start-installation)
   2. [Manual Installation Process](#manual-installation-process)
   3. [Docker Deployment](#docker-deployment)
10. [Security and Authentication](#security-and-authentication)
11. [Performance Optimization](#performance-optimization)
12. [Troubleshooting and Support](#troubleshooting-and-support)
13. [Revision History](#revision-history)

---

## Introduction
The Novellus Loan Management System is a financial platform for calculating, tracking, and reporting loan applications. It supports bridge, term, and development loans and provides tools for administrators and analysts to configure and monitor the system.

---

## Landing Page and System Overview
The application redirects new visitors to the calculator interface after authentication. The landing page describes system capabilities and offers direct access to the primary calculation dashboard.

---

## Loan Calculator Operations
1. **Access the Calculator** – Navigate to `/calculator` once logged in.
2. **Select Loan Type** – Choose Bridge, Term, Development, or Development 2.
3. **Enter Parameters** – Supply loan amount, fees, interest rate, and related details.
4. **Review Results** – The interface displays gross amount, interest, fees, and repayment schedule.
5. **Save or Download** – Persist results to the database or export to PDF.

---

## Loan History Management
- Access stored applications through `/loan_history`.
- Search by customer, loan reference, or date.
- View, edit, or archive existing loans.
- Download historical calculations for auditing or review.

---

## Power BI Integration and Automation
The system exposes endpoints and scripts to refresh Power BI datasets and schedules. Automated refresh scripts (`powerbi_refresh.py`) may be configured for cron or Azure Functions.

---

## System Administration
Administrative users manage accounts, permissions, and application settings through the administration interface. Database initialization scripts and configuration files support environment-specific deployments.

---

## Net-to-Gross Calculation Formulas
### Bridge Loan Formulas
**Bridge Retained Interest**
```
Gross = (Net + Legals + Site) / (1 - Arrangement Fee - Interest rate - Title insurance)
```
**Bridge Serviced (Service Only)**
```
Gross = (Net + Legals + Site) / (1 - Arrangement Fee - (Interest rate/12) - Title insurance)
```
**Bridge Service + Capital**
```
Gross = (Net + Legals + Site) / (1 - Arrangement Fee - Title insurance)
```
**Bridge Flexible Payment**
```
Gross = (Net + Legals + Site) / (1 - Arrangement Fee - Title insurance)
```
**Bridge Capital Payment Only**
```
Gross = (Net + Legals + Site) / (1 - Arrangement Fee - Interest rate - Title insurance)
```

### Term Loan Formulas
Term loans mirror the bridge loan formulas for each payment structure.

### Development Loan Methodology
Development loans use an iterative goal seek approach:
1. Specify the target net amount.
2. Iteratively compute the gross amount: `Net = Gross - Arrangement Fee - Legal Fees - Interest`.
3. Adjust the gross value until the net reaches the target within £0.01.
4. Interest is calculated per tranche using daily compounding:
```
Interest = Tranche1 × ((1 + daily_rate)^days1 - 1)
         + Tranche2 × ((1 + daily_rate)^days2 - 1) + …
```
where `daily_rate = Annual Rate / 365` and `days` is the number of days from tranche release to loan end.

---

## Calculation Logic Reference
- **Core Engine**: `calculations.py`
- **Loan Models**: `models.py`
- **Utilities**: `utils.py`
- **Templates**: stored in `templates/`
These components govern business logic and user interface rendering.

---

## Installation and Deployment
### Quick Start Installation
**Linux/macOS**
```bash
curl -O install.sh
chmod +x install.sh
./install.sh
./start.sh
```
**Windows**
```cmd
install.bat
start.bat
```

### Manual Installation Process
**Prerequisites**
- Python 3.8+
- PostgreSQL 12+
- Git
- Node.js 16+ (optional for frontend assets)

**Database Setup**
1. Install PostgreSQL.
2. Create database: `createdb novellus_loans`.
3. Create user: `createuser -P novellus_user`.
4. Grant permissions: `GRANT ALL ON DATABASE novellus_loans TO novellus_user;`.
5. Enable SSL in `postgresql.conf`.

**Python Environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r deploy_requirements.txt
```

**Application Configuration**
```bash
cp production.env.template .env
nano .env  # Set DATABASE_URL and SESSION_SECRET
python database_init.py
gunicorn --bind 0.0.0.0:5000 main:app
```

### Docker Deployment
Dockerfile excerpt:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r deploy_requirements.txt
RUN python database_init.py
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
```
Deploy to Azure Container Apps:
```bash
az containerapp up \
  --name novellus-loans \
  --resource-group novellus-rg \
  --environment novellus-env \
  --image novellus-loans:latest \
  --target-port 5000
```

---

## Security and Authentication
### Database Security
- SSL encryption required for all connections.
- Use dedicated database users with limited privileges.
- Implement connection pooling with timeouts.
- Schedule regular backups.

### Session Management
- Authentication handled by Flask-Login.
- Optional JWT support for API endpoints.
- Configurable session timeouts.
- CSRF protection enabled.

---

## Performance Optimization
### Server Configuration
- Gunicorn recommended for production.
- Configure worker processes to scale with CPU cores.
- Optimize request handling for concurrent calculations.
- Monitor memory usage for large datasets.

### Database Optimization
- Index frequently queried fields.
- Use efficient SQLAlchemy queries.
- Manage connections through pooling and recycling.
- Track query performance for tuning.

---

## Troubleshooting and Support
- Check application logs for stack traces or configuration issues.
- Verify database connectivity and credentials.
- For Power BI problems, confirm API keys and dataset IDs.
- Contact the development team for unresolved issues.

---

## Revision History
| Version | Date           | Notes                             |
|---------|----------------|-----------------------------------|
| 2.1.0   | July 30, 2025  | Initial professional rewrite.     |

*End of User Manual*
