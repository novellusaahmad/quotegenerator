# Novellus Loan Management System – User Manual

*Version 2.2.0 | Last Updated: September 3, 2025*

---

## Table of Contents
1. [Introduction](#introduction)
2. [Quick Tour](#quick-tour)
3. [Running a Loan Calculation](#running-a-loan-calculation)
4. [Viewing Loan History](#viewing-loan-history)
5. [Power BI Automation](#power-bi-automation)
6. [Administrator Tools](#administrator-tools)
7. [Net-to-Gross Formulas](#net-to-gross-formulas)
    1. [Bridge Loans](#bridge-loans)
    2. [Term Loans](#term-loans)
    3. [Development Loans](#development-loans)
8. [Core Components](#core-components)
9. [Installation and Deployment](#installation-and-deployment)
    1. [Quick Start](#quick-start)
    2. [Manual Setup](#manual-setup)
    3. [Docker](#docker)
10. [Security](#security)
11. [Performance Tips](#performance-tips)
12. [Troubleshooting](#troubleshooting)
13. [Revision History](#revision-history)

---

## Introduction
The Novellus Loan Management System helps lenders calculate, store and report on bridge, term and development loans. This guide walks through everyday tasks for end users and administrators.

---

## Quick Tour
Authenticated users are redirected to the calculator page. The landing page briefly describes capabilities and links to the main dashboard.

---

## Running a Loan Calculation
1. **Open** `/calculator`.
2. **Choose** a loan type: Bridge, Term, Development or Development 2.
3. **Provide** the loan amount, fees, interest rate and other required values.
4. **Review** the gross figure, fee breakdown and repayment schedule.
5. **Save** the loan or **download** the result as a PDF.

---

## Viewing Loan History
- Go to `/loan_history`.
- Search by borrower name, reference or creation date.
- Open a record to edit, archive or download the original calculation.

---

## Power BI Automation
Scripts such as `powerbi_refresh.py` can trigger dataset refreshes. They may run on cron, Windows Task Scheduler or Azure Functions.

---

## Administrator Tools
Administrators manage accounts, permissions and environment settings. Initialization scripts and configuration files support different deployment targets.

---

## Net-to-Gross Formulas

### Bridge Loans
**Retained Interest**
```
Gross = (Net + Legals + Site) / (1 - Arrangement Fee - Interest rate - Title insurance)
```
**Serviced (Service Only)**
```
Gross = (Net + Legals + Site) / (1 - Arrangement Fee - (Interest rate/12) - Title insurance)
```
**Service & Capital**
```
Gross = (Net + Legals + Site) / (1 - Arrangement Fee - Title insurance)
```
**Flexible Payment**
```
Gross = (Net + Legals + Site) / (1 - Arrangement Fee - Title insurance)
```
**Capital Payment Only**
```
Gross = (Net + Legals + Site) / (1 - Arrangement Fee - Interest rate - Title insurance)
```

### Term Loans
The same formulas apply to term loans for each payment structure.

### Development Loans
Development loans use a goal‑seek approach:

1. Enter the target net figure.
2. Iteratively compute: `Net = Gross - Arrangement Fee - Legal Fees - Interest`.
3. Adjust `Gross` until `Net` is within £0.01 of the target.
4. Interest is calculated per tranche using daily compounding:
```
Interest = Σ tranche_amount × ((1 + daily_rate)^days - 1)
```
where `daily_rate = Annual Rate / 365`.

---

## Core Components
- **Business Logic:** `calculations.py`
- **Data Models:** `models.py`
- **Helpers:** `utils.py`
- **HTML Templates:** `templates/`

---

## Installation and Deployment

### Quick Start
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

### Manual Setup

**Prerequisites**

- Python 3.8+
- PostgreSQL 12+
- Git
- Optional: Node.js 16+ for frontend builds

**Database**

1. Install PostgreSQL.
2. `createdb novellus_loans`
3. `createuser -P novellus_user`
4. `GRANT ALL ON DATABASE novellus_loans TO novellus_user;`
5. Enable SSL in `postgresql.conf`.

**Python Environment**
```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate       # Windows
pip install -r deploy_requirements.txt
```

**Application Configuration**
```bash
cp production.env.template .env
nano .env    # Set DATABASE_URL and SESSION_SECRET
python database_init.py
gunicorn --bind 0.0.0.0:5000 main:app
```

### Docker
Example `Dockerfile`:
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

## Security
### Database
- Enforce SSL.
- Use accounts with least privilege.
- Pool connections and apply timeouts.
- Back up regularly.

### Sessions
- Uses Flask‑Login with optional JWT.
- Configurable expiration.
- CSRF protection enabled.

---

## Performance Tips
### Server
- Use Gunicorn in production.
- Configure workers for available CPU cores.
- Monitor memory use for large calculations.

### Database
- Index columns used for filtering.
- Prefer efficient SQLAlchemy queries.
- Tune the connection pool and recycle settings.

---

## Troubleshooting
- Review application logs for errors.
- Confirm database credentials and connectivity.
- For Power BI issues, verify API keys and dataset IDs.
- Contact the development team for additional support.

---

## Revision History
| Version | Date            | Notes                               |
|--------:|-----------------|-------------------------------------|
| 2.2.0   | Sep 3, 2025     | Rewritten manual for clarity.       |
| 2.1.0   | Jul 30, 2025    | Initial professional rewrite.       |

*End of User Manual*

