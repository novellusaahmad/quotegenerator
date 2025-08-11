#!/bin/bash

echo "============================================================"
echo "Starting Novellus Loan Management System"
echo "============================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found. Please run ./install_clean.sh first"
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_error ".env file not found. Please run ./install_clean.sh first"
    exit 1
fi

# Load environment variables (but we'll override DATABASE_URL for on-premise)
if [ -f ".env" ]; then
    source .env
fi

# Power BI On-Premise Configuration Setup
print_status "Preparing Power BI on-premise configuration..."

# Check if this is Replit environment
if [ -n "$REPL_ID" ]; then
    print_status "Replit environment detected - using cloud database with on-premise documentation"
    
    # Keep existing cloud database but generate on-premise instructions
    CURRENT_DB_URL="$DATABASE_URL"
    
    print_status "Current database: Cloud PostgreSQL (for development)"
    print_status "Generating on-premise Power BI configuration for deployment..."
    
else
    # This is a real on-premise environment - configure PostgreSQL
    print_status "On-premise environment detected - configuring local PostgreSQL..."
    
    # Install PostgreSQL if not present
    if ! command -v psql &> /dev/null; then
        print_status "Installing PostgreSQL..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y postgresql postgresql-contrib postgresql-server-dev-all
        elif command -v yum &> /dev/null; then
            sudo yum install -y postgresql postgresql-server postgresql-contrib postgresql-devel
            sudo postgresql-setup initdb
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y postgresql postgresql-server postgresql-contrib postgresql-devel
            sudo postgresql-setup --initdb
        else
            print_error "Could not install PostgreSQL automatically. Please install manually."
            exit 1
        fi
    fi

    # Start PostgreSQL service
    print_status "Starting PostgreSQL service..."
    if command -v systemctl &> /dev/null; then
        sudo systemctl enable postgresql 2>/dev/null || true
        sudo systemctl start postgresql 2>/dev/null || true
        sleep 3
    elif command -v service &> /dev/null; then
        sudo service postgresql start 2>/dev/null || true
        sleep 3
    fi

    # Create database and user for on-premise deployment
    print_status "Creating on-premise database configuration..."
    sudo -u postgres psql -c "CREATE DATABASE IF NOT EXISTS novellus_loans;" 2>/dev/null || \
    sudo -u postgres createdb novellus_loans 2>/dev/null || true

    sudo -u postgres psql -c "CREATE USER IF NOT EXISTS novellus_user WITH PASSWORD 'novellus_secure_2025';" 2>/dev/null || \
    sudo -u postgres psql -c "CREATE USER novellus_user WITH PASSWORD 'novellus_secure_2025';" 2>/dev/null || true

    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE novellus_loans TO novellus_user;" 2>/dev/null || true
    sudo -u postgres psql -c "ALTER USER novellus_user CREATEDB;" 2>/dev/null || true

    # Configure PostgreSQL for external Power BI access
    print_status "Configuring PostgreSQL for Power BI external access..."

    # Find PostgreSQL configuration directory
    PG_VERSION=$(sudo -u postgres psql -t -c "SELECT version();" | grep -oE '[0-9]+\.[0-9]+' | head -1)
    PG_CONFIG_DIR="/etc/postgresql/$PG_VERSION/main"

    if [ ! -d "$PG_CONFIG_DIR" ]; then
        # Try alternative paths
        PG_CONFIG_DIR=$(sudo find /etc/postgresql -name "postgresql.conf" -exec dirname {} \; 2>/dev/null | head -1)
    fi

    if [ -d "$PG_CONFIG_DIR" ]; then
        print_status "Configuring PostgreSQL for external connections..."
        
        # Backup original files
        sudo cp "$PG_CONFIG_DIR/postgresql.conf" "$PG_CONFIG_DIR/postgresql.conf.backup" 2>/dev/null || true
        sudo cp "$PG_CONFIG_DIR/pg_hba.conf" "$PG_CONFIG_DIR/pg_hba.conf.backup" 2>/dev/null || true
        
        # Configure for external access
        sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "$PG_CONFIG_DIR/postgresql.conf"
        sudo sed -i "s/listen_addresses = 'localhost'/listen_addresses = '*'/" "$PG_CONFIG_DIR/postgresql.conf"
        
        # Enable SSL
        sudo sed -i "s/#ssl = off/ssl = on/" "$PG_CONFIG_DIR/postgresql.conf"
        sudo sed -i "s/ssl = off/ssl = on/" "$PG_CONFIG_DIR/postgresql.conf"
        
        # Add Power BI access rules to pg_hba.conf
        if ! grep -q "Power BI External Access" "$PG_CONFIG_DIR/pg_hba.conf" 2>/dev/null; then
            cat << EOF | sudo tee -a "$PG_CONFIG_DIR/pg_hba.conf"

# Power BI External Access Configuration
hostssl all novellus_user 0.0.0.0/0 md5
host all novellus_user 0.0.0.0/0 md5
hostssl all novellus_user 192.168.0.0/16 md5
hostssl all novellus_user 10.0.0.0/8 md5
hostssl all novellus_user 172.16.0.0/12 md5
EOF
        fi
        
        # Restart PostgreSQL
        print_status "Restarting PostgreSQL with new configuration..."
        sudo systemctl restart postgresql 2>/dev/null || sudo service postgresql restart 2>/dev/null || true
        sleep 3
    fi

    # Configure firewall for PostgreSQL port
    print_status "Opening firewall for PostgreSQL port 5432..."
    if command -v ufw &> /dev/null; then
        sudo ufw allow 5432/tcp 2>/dev/null || true
    elif command -v firewall-cmd &> /dev/null; then
        sudo firewall-cmd --permanent --add-port=5432/tcp 2>/dev/null || true
        sudo firewall-cmd --reload 2>/dev/null || true
    fi

    # Override DATABASE_URL for on-premise use
    print_status "Switching to on-premise database configuration..."
    export DATABASE_URL="postgresql://novellus_user:novellus_secure_2025@localhost:5432/novellus_loans"
    export PGHOST="localhost"
    export PGPORT="5432"
    export PGDATABASE="novellus_loans"
    export PGUSER="novellus_user" 
    export PGPASSWORD="novellus_secure_2025"

    print_status "Database URL updated: $DATABASE_URL"
fi

# Update .env file for on-premise configuration
if [ -f ".env" ]; then
    # Create backup
    cp .env .env.cloud.backup
    
    # Update .env with on-premise settings
    cat > .env << EOF
# Novellus Loan Management System - On-Premise Configuration
SESSION_SECRET=novellus-loan-management-secret-key-2025

# On-Premise PostgreSQL Database Configuration
DATABASE_URL=postgresql://novellus_user:novellus_secure_2025@localhost:5432/novellus_loans

# PostgreSQL connection parameters for Power BI external access
PGHOST=localhost
PGPORT=5432
PGDATABASE=novellus_loans
PGUSER=novellus_user
PGPASSWORD=novellus_secure_2025

# Power BI SSL Configuration
PG_SSLMODE=prefer
ALLOW_EXTERNAL_CONNECTIONS=true

FLASK_ENV=development
FLASK_DEBUG=True
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
WEASYPRINT_ENABLED=False
EOF
fi

# Test database connection
print_status "Testing database connection..."

# Create a simple test script that uses the environment variables
cat > test_db_connection.py << 'EOF'
import os
import psycopg2
try:
    database_url = os.environ.get('DATABASE_URL')
    # Mask password for display
    display_url = database_url
    if '@' in display_url:
        parts = display_url.split('@')
        user_pass = parts[0].split('//')[-1]
        if ':' in user_pass:
            user, password = user_pass.split(':', 1)
            display_url = display_url.replace(f':{password}@', ':***@')
    
    print(f"Testing connection to: {display_url}")
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    cursor.execute("SELECT current_database(), current_user;")
    db_name, user = cursor.fetchone()
    print(f"✅ Connected to database: {db_name} as user: {user}")
    cursor.close()
    conn.close()
    print("✅ Database connection successful")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    exit(1)
EOF

python test_db_connection.py
if [ $? -eq 0 ]; then
    print_status "Database configured successfully"
    rm test_db_connection.py
else
    print_error "Database connection failed"
    rm test_db_connection.py
    exit 1
fi

# Initialize database if needed
print_status "Initializing database..."
python database_init.py

# Check if main.py exists
if [ ! -f "main.py" ]; then
    print_error "main.py not found in current directory"
    exit 1
fi

# Get server IP for Power BI connection info
SERVER_IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "localhost")

# Display startup information with environment-specific Power BI details
echo ""
echo "============================================================"
echo "Novellus Loan Management System Starting..."
echo "============================================================"

if [ -n "$REPL_ID" ]; then
    echo "Environment: Replit Development"
    echo "Database: Cloud PostgreSQL (development)"
    echo "Server: Gunicorn production server"
    echo "Application URL: http://0.0.0.0:5000"
    echo ""
    echo "============================================================"
    echo "On-Premise Power BI Configuration (for deployment)"
    echo "============================================================"
    echo "When deploying to your on-premise server, use these settings:"
    echo ""
    echo "Database Host: [YOUR_SERVER_IP]"
    echo "Database Port: 5432"
    echo "Database Name: novellus_loans"
    echo "Username: novellus_user"
    echo "Password: novellus_secure_2025"
    echo ""
    echo "Power BI Connection String (SSL Enabled):"
    echo "Server=[YOUR_SERVER_IP];Database=novellus_loans;Port=5432;User Id=novellus_user;Password=novellus_secure_2025;SSL Mode=Require;Trust Server Certificate=true;"
    echo ""
    echo "Power BI Connection String (SSL Disabled - if certificate issues):"
    echo "Server=[YOUR_SERVER_IP];Database=novellus_loans;Port=5432;User Id=novellus_user;Password=novellus_secure_2025;SSL Mode=Disable;"
    echo ""
    echo "📋 See ONPREMISE_POWERBI_SETUP.md for complete deployment instructions"
else
    echo "Environment: On-Premise Production"
    echo "Database: PostgreSQL (on-premise)"
    echo "Server: Gunicorn production server"
    echo "Application URL: http://0.0.0.0:5000"
    echo ""
    echo "============================================================"
    echo "Power BI Connection Information"
    echo "============================================================"
    echo "Database Host: $SERVER_IP"
    echo "Database Port: 5432"
    echo "Database Name: novellus_loans"
    echo "Username: novellus_user"
    echo "Password: novellus_secure_2025"
    echo ""
    echo "Power BI Connection String (SSL Enabled):"
    echo "Server=$SERVER_IP;Database=novellus_loans;Port=5432;User Id=novellus_user;Password=novellus_secure_2025;SSL Mode=Require;Trust Server Certificate=true;"
    echo ""
    echo "Power BI Connection String (SSL Disabled - if certificate issues):"
    echo "Server=$SERVER_IP;Database=novellus_loans;Port=5432;User Id=novellus_user;Password=novellus_secure_2025;SSL Mode=Disable;"
    echo ""
    echo "Power BI Desktop Setup:"
    echo "1. Open Power BI Desktop"
    echo "2. Get Data → Database → PostgreSQL database"
    echo "3. Server: $SERVER_IP:5432"
    echo "4. Database: novellus_loans"
    echo "5. Username: novellus_user"
    echo "6. Password: novellus_secure_2025"
fi

echo "============================================================"
echo ""

# Start the application
print_status "Starting loan calculator application..."

# Try Gunicorn first (production server)
if command -v gunicorn &> /dev/null; then
    print_status "Starting with Gunicorn production server..."
    gunicorn --bind 0.0.0.0:8502 --workers 2 --timeout 120 --reload main:app
elif command -v waitress-serve &> /dev/null; then
    print_status "Starting with Waitress server..."
    waitress-serve --host=0.0.0.0 --port=5000 main:app
else
    print_status "Starting with Flask development server..."
    export FLASK_APP=main.py
    export FLASK_ENV=production
    python -m flask run --host=0.0.0.0 --port=5000
fi
