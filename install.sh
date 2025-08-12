#!/bin/bash

echo "============================================================"
echo "Novellus Loan Management System - Clean Installation"
echo "============================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    echo "Please install Python 3.8+ using your package manager:"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "  macOS: brew install python3"
    exit 1
fi

print_status "Python found: $(python3 --version)"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed"
    echo "Please install pip3 using your package manager:"
    echo "  Ubuntu/Debian: sudo apt install python3-pip"
    echo "  CentOS/RHEL: sudo yum install python3-pip"
    echo "  macOS: pip3 should be installed with Python"
    exit 1
fi

print_status "Pip found: $(pip3 --version)"

# Create virtual environment
print_status "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    print_error "Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
python -m pip install --upgrade pip

# Install system dependencies and PostgreSQL
print_status "Checking and installing system dependencies..."
if command -v apt-get &> /dev/null; then
    # Ubuntu/Debian
    print_status "Detected Ubuntu/Debian system"
    print_status "Installing system dependencies..."
    sudo apt-get update -qq
    sudo apt-get install -y build-essential python3-dev libpq-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev libjpeg-dev zlib1g-dev
    
    # Install PostgreSQL
    print_status "Installing PostgreSQL database server..."
    if ! sudo apt-get install -y postgresql postgresql-contrib postgresql-client; then
        print_error "Failed to install PostgreSQL"
        exit 1
    fi
    
    sudo systemctl enable postgresql
    sudo systemctl start postgresql

elif command -v yum &> /dev/null; then
    # CentOS/RHEL
    print_status "Detected CentOS/RHEL system"
    sudo yum groupinstall -y "Development Tools"
    sudo yum install -y python3-devel postgresql-devel libffi-devel openssl-devel libxml2-devel libxslt-devel libjpeg-devel zlib-devel
    
    # Install PostgreSQL
    sudo yum install -y postgresql postgresql-server postgresql-contrib
    sudo postgresql-setup initdb
    sudo systemctl enable postgresql
    sudo systemctl start postgresql

elif command -v dnf &> /dev/null; then
    # Fedora
    print_status "Detected Fedora system"
    sudo dnf groupinstall -y "Development Tools"
    sudo dnf install -y python3-devel postgresql-devel libffi-devel openssl-devel libxml2-devel libxslt-devel libjpeg-devel zlib-devel
    
    # Install PostgreSQL
    sudo dnf install -y postgresql postgresql-server postgresql-contrib
    sudo postgresql-setup --initdb
    sudo systemctl enable postgresql
    sudo systemctl start postgresql

elif command -v brew &> /dev/null; then
    # macOS
    print_status "Detected macOS system"
    brew install postgresql libpq pkg-config
    brew services start postgresql
else
    print_warning "Package manager not detected. Please install system dependencies manually."
fi

# Wait for PostgreSQL to be ready
print_status "Waiting for PostgreSQL to be ready..."
sleep 5

# Configure PostgreSQL database
print_status "Configuring PostgreSQL database..."
sudo -u postgres psql -c "DROP DATABASE IF EXISTS novellus_loans;" 2>/dev/null || true
sudo -u postgres psql -c "DROP USER IF EXISTS novellus_user;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE USER novellus_user WITH PASSWORD 'novellus_secure_2025';"
sudo -u postgres psql -c "CREATE DATABASE novellus_loans OWNER novellus_user;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE novellus_loans TO novellus_user;"

# Configure SSL certificate for PostgreSQL
print_status "Configuring PostgreSQL SSL certificate..."
PGDATA=$(sudo -u postgres psql -t -c "SHOW data_directory;" | tr -d ' \n')
if [ -n "$PGDATA" ]; then
    if [ ! -f "$PGDATA/server.crt" ] || [ ! -f "$PGDATA/server.key" ]; then
        print_status "Generating self-signed certificate..."

        CERT_DOMAIN="${POSTGRES_SSL_CN:-$(hostname -f 2>/dev/null || hostname)}"
        if [ ${#CERT_DOMAIN} -gt 64 ]; then
            print_warning "Hostname '${CERT_DOMAIN}' exceeds 64 characters; truncating for CN"
        fi
        CERT_CN="${CERT_DOMAIN:0:64}"

        sudo openssl req -x509 -nodes -days 365 \
            -newkey rsa:2048 \
            -keyout "$PGDATA/server.key" \
            -out "$PGDATA/server.crt" \
            -subj "/CN=${CERT_CN}" \
            -addext "subjectAltName=DNS:${CERT_DOMAIN}"
        sudo chown postgres:postgres "$PGDATA/server.key" "$PGDATA/server.crt"
        sudo chmod 600 "$PGDATA/server.key"
    else
        print_warning "Existing certificate found, skipping generation"
    fi

    PGCONF=$(sudo -u postgres psql -t -c "SHOW config_file;" | tr -d ' \n')
    if [ -f "$PGCONF" ]; then
        sudo sed -i "s/^#ssl = off/ssl = on/" "$PGCONF"
        sudo sed -i "s/^#ssl_cert_file.*/ssl_cert_file = 'server.crt'/" "$PGCONF"
        sudo sed -i "s/^#ssl_key_file.*/ssl_key_file = 'server.key'/" "$PGCONF"
        print_status "SSL enabled in PostgreSQL configuration"
    else
        print_warning "PostgreSQL configuration file not found; SSL may not be enabled"
    fi

    sudo systemctl restart postgresql
else
    print_warning "Could not determine PostgreSQL data directory; skipping SSL setup"
fi

# Install Python dependencies
print_status "Installing Python dependencies..."
if [ -f "deploy_requirements.txt" ]; then
    pip install -r deploy_requirements.txt
elif [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    # Install core dependencies with specific versions for compatibility
    pip install "flask>=2.3.0" "flask-sqlalchemy>=3.0.0" "flask-login>=0.6.0" "flask-cors>=4.0.0" 
    pip install "psycopg2-binary>=2.9.0" "python-dotenv>=1.0.0" "gunicorn>=21.0.0"
    pip install "pandas>=2.0.0" "numpy>=1.24.0" "openpyxl>=3.1.0" "xlsxwriter>=3.1.0" 
    pip install "reportlab>=4.0.0" "python-docx>=0.8.11" "mammoth>=1.6.0"
    # WeasyPrint optional - may fail on some systems
    pip install weasyprint || print_warning "WeasyPrint installation failed, but system will work without it"
fi

# Create .env file
print_status "Creating environment configuration..."
cat > .env << EOF
DATABASE_URL=postgresql://novellus_user:novellus_secure_2025@localhost/novellus_loans?sslmode=require
PG_SSLMODE=require
SESSION_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
FLASK_ENV=production
FLASK_DEBUG=False
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads
ALLOWED_EXTENSIONS=xlsx,xls,csv,pdf,docx,doc
EOF

# Create uploads directory
mkdir -p uploads
mkdir -p reports_output

# Initialize database
print_status "Initializing database..."
python database_init.py

# Test installation
print_status "Testing installation..."
if python -c "import flask, psycopg2, pandas, numpy; from app import app; print('All dependencies imported successfully')"; then
    print_status "✅ Installation completed successfully!"
    echo ""
    echo "============================================================"
    echo "Installation Summary:"
    echo "- PostgreSQL database: novellus_loans"
    echo "- Database user: novellus_user"
    echo "- Virtual environment: ./venv"
    echo "- Configuration: .env file created"
    echo "- SSL: Self-signed certificate installed for PostgreSQL"
    echo "============================================================"
    echo ""
    echo "To start the application, run:"
    echo "  ./start_clean.sh"
    echo ""
    echo "Power BI connection examples:"
    echo "  SSL Enabled:  Server=[SERVER_IP];Database=novellus_loans;Port=5432;User Id=novellus_user;Password=novellus_secure_2025;SSL Mode=Require;Trust Server Certificate=true;"
    echo "  SSL Disabled: Server=[SERVER_IP];Database=novellus_loans;Port=5432;User Id=novellus_user;Password=novellus_secure_2025;SSL Mode=Disable;"
    echo ""
else
    print_error "Installation verification failed"
    exit 1
fi
