# Power BI SSL Certificate Troubleshooting Guide

## 🔒 SSL Certificate Error Solutions

### ❌ **Error Message**
```
"The remote certificate is invalid according to the validation procedure."
```

This error occurs when Power BI Service cannot validate the SSL certificate from your on-premise PostgreSQL database.

> **Note:** The `start.sh` script automatically detects whether a PostgreSQL SSL certificate is present. If none is found, it sets `PG_SSLMODE=disable` in your `.env` file and prints a ready-to-use Power BI connection string with `SSL Mode=Disable`.

---

## 🚀 **Quick Fixes** (Recommended Order)

### 1️⃣ **Disable SSL Mode** (Fastest Solution)

#### Power BI Desktop
1. When connecting, use this connection string:
```
Server=[YOUR_SERVER_IP];Database=novellus_loans;Port=5432;User Id=novellus_user;Password=novellus_secure_2025;SSL Mode=Disable;
```

#### Power BI Service Direct Connection
1. In Power BI Service data source settings:
   - **Server**: [YOUR_SERVER_IP]
   - **Database**: novellus_loans
   - **Authentication**: Database
   - **Username**: novellus_user
   - **Password**: novellus_secure_2025
   - **Connection String Parameters**: `SSL Mode=Disable;`

### 2️⃣ **Trust Server Certificate** (SSL Enabled)

Use this connection string to keep SSL but ignore certificate validation:
```
Server=[YOUR_SERVER_IP];Database=novellus_loans;Port=5432;User Id=novellus_user;Password=novellus_secure_2025;SSL Mode=Require;Trust Server Certificate=true;
```

### 3️⃣ **Use On-Premises Data Gateway** (Recommended for Production)

#### Setup Gateway
1. Download and install **On-Premises Data Gateway** on your server
2. Configure data source in gateway:
   - **Data Source Type**: PostgreSQL  
   - **Server**: localhost
   - **Database**: novellus_loans
   - **Username**: novellus_user
   - **Password**: novellus_secure_2025
   - **SSL**: Disabled (internal connection)

#### Power BI Service Configuration
1. In Power BI Service, create dataset using gateway connection
2. SSL is handled internally by the gateway

---

## 🔧 **Advanced SSL Configuration**

### Generate Valid SSL Certificate

If you need proper SSL certificates, run these commands on your server:

```bash
# Generate self-signed certificate with server IP
sudo openssl req -new -x509 -days 365 -nodes -text \
  -out server.crt \
  -keyout server.key \
  -subj "/CN=[YOUR_SERVER_IP]"

# Set proper ownership and permissions
sudo chown postgres:postgres server.crt server.key
sudo chmod 600 server.key
sudo chmod 644 server.crt

# Move to PostgreSQL directory
PG_VERSION=$(sudo -u postgres psql -t -c "SELECT version();" | grep -oE '[0-9]+\.[0-9]+' | head -1)
sudo mv server.crt server.key /var/lib/postgresql/$PG_VERSION/main/

# Update PostgreSQL configuration
sudo sed -i "s/#ssl_cert_file = 'server.crt'/ssl_cert_file = 'server.crt'/" /etc/postgresql/$PG_VERSION/main/postgresql.conf
sudo sed -i "s/#ssl_key_file = 'server.key'/ssl_key_file = 'server.key'/" /etc/postgresql/$PG_VERSION/main/postgresql.conf

# Restart PostgreSQL
sudo systemctl restart postgresql
```

---

## 🧪 **Test Connection Methods**

### Command Line Test
```bash
# Test SSL disabled
psql "host=[YOUR_SERVER_IP] port=5432 dbname=novellus_loans user=novellus_user password=novellus_secure_2025 sslmode=disable"

# Test SSL enabled
psql "host=[YOUR_SERVER_IP] port=5432 dbname=novellus_loans user=novellus_user password=novellus_secure_2025 sslmode=require"
```

### Python Test Script
```python
import psycopg2

# Test SSL disabled
try:
    conn = psycopg2.connect(
        host="[YOUR_SERVER_IP]",
        port=5432,
        database="novellus_loans", 
        user="novellus_user",
        password="novellus_secure_2025",
        sslmode="disable"
    )
    print("✅ SSL Disabled connection successful")
    conn.close()
except Exception as e:
    print(f"❌ SSL Disabled connection failed: {e}")

# Test SSL enabled
try:
    conn = psycopg2.connect(
        host="[YOUR_SERVER_IP]",
        port=5432,
        database="novellus_loans",
        user="novellus_user", 
        password="novellus_secure_2025",
        sslmode="require"
    )
    print("✅ SSL Enabled connection successful")
    conn.close()
except Exception as e:
    print(f"❌ SSL Enabled connection failed: {e}")
```

---

## 🎯 **Power BI Service Specific Solutions**

### Method 1: Connection String Parameters
In Power BI Service data source settings, add these to "Connection String Parameters":
```
SSL Mode=Disable;Timeout=30;CommandTimeout=300;
```

### Method 2: Advanced Connection Properties
```
Server=[YOUR_SERVER_IP]
Database=novellus_loans
Port=5432
SSL Mode=disable
Trust Server Certificate=true
Connection Timeout=30
Command Timeout=300
```

### Method 3: Gateway Configuration
```
Data Source Name: Novellus Loans DB
Data Source Type: PostgreSQL
Server: localhost
Database: novellus_loans
Authentication Method: Basic
Username: novellus_user
Password: novellus_secure_2025
Privacy Level: Organizational
```

---

## 🔍 **Debugging Steps**

### 1. Check PostgreSQL SSL Status
```bash
sudo -u postgres psql -c "SHOW ssl;"
sudo -u postgres psql -c "SELECT * FROM pg_stat_ssl;"
```

### 2. Check Certificate Files
```bash
sudo ls -la /var/lib/postgresql/*/main/server.*
sudo openssl x509 -in /var/lib/postgresql/*/main/server.crt -text -noout
```

### 3. Check PostgreSQL Logs
```bash
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### 4. Test Port Connectivity
```bash
telnet [YOUR_SERVER_IP] 5432
nmap -p 5432 [YOUR_SERVER_IP]
```

---

## ⚠️ **Security Considerations**

### SSL Disabled (Development Only)
- **Pros**: No certificate issues, easy setup
- **Cons**: Data transmitted in plain text
- **Use for**: Development, internal networks only

### SSL Enabled with Trust Certificate
- **Pros**: Data encrypted, works with self-signed certificates
- **Cons**: Vulnerable to man-in-the-middle attacks
- **Use for**: Internal production networks

### Proper SSL Certificates
- **Pros**: Full security, production-ready
- **Cons**: More complex setup, requires certificate management
- **Use for**: Production systems with external access

---

## 📞 **Still Having Issues?**

### Common Problems:
1. **Firewall blocking**: Ensure port 5432 is open
2. **PostgreSQL not listening**: Check `listen_addresses = '*'` 
3. **Authentication failure**: Verify pg_hba.conf has correct rules
4. **Network routing**: Test with telnet/nmap first

### Quick Diagnostic:
```bash
# Run the complete diagnostic
./start.sh
# Check the connection information displayed
# Try the SSL disabled connection string first
```

---

*For immediate resolution, use SSL Mode=Disable. For production deployment, implement proper SSL certificates or use On-Premises Data Gateway.*