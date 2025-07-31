# On-Premise Power BI Database Access

## Overview
This system is configured for on-premise PostgreSQL deployment with external Power BI access. All configuration is automatically handled by the `start.sh` script.

## Automatic Configuration by start.sh

When you run `./start.sh`, the script automatically:

1. **Installs PostgreSQL** (if not present)
2. **Creates database and user**:
   - Database: `novellus_loans`
   - User: `novellus_user`
   - Password: `novellus_secure_2025`
3. **Configures external access**:
   - Updates `postgresql.conf` for external connections
   - Modifies `pg_hba.conf` for Power BI access
   - Enables SSL encryption
4. **Opens firewall** for port 5432
5. **Updates environment** variables for on-premise use
6. **Displays Power BI connection** information

## Power BI Connection Details

After running `./start.sh`, you'll see the connection information displayed:

```
============================================================
Power BI Connection Information
============================================================
Database Host: [YOUR_SERVER_IP]
Database Port: 5432
Database Name: novellus_loans
Username: novellus_user
Password: novellus_secure_2025

Power BI Connection String:
Server=[YOUR_SERVER_IP];Database=novellus_loans;Port=5432;User Id=novellus_user;Password=novellus_secure_2025;SSL Mode=Prefer;Trust Server Certificate=true;
```

## Power BI Desktop Setup

1. Open Power BI Desktop
2. Click **Get Data** → **Database** → **PostgreSQL database**
3. Enter connection details:
   - **Server**: `[YOUR_SERVER_IP]:5432`
   - **Database**: `novellus_loans`
4. Choose **Database** authentication
5. Enter credentials:
   - **User name**: `novellus_user`
   - **Password**: `novellus_secure_2025`
6. Click **Connect**

## Power BI Service (Cloud) Setup

### Option 1: On-Premises Data Gateway
1. Install On-Premises Data Gateway on your server
2. Configure PostgreSQL data source:
   - **Server**: `localhost` (from gateway perspective)
   - **Database**: `novellus_loans`
   - **Username**: `novellus_user`
   - **Password**: `novellus_secure_2025`

### Option 2: Direct Connection (if server is internet-accessible)
Use the connection string provided by `start.sh` in Power BI Service.

## Database Tables Available

- **loan_summary**: Main loan records with calculations
- **payment_schedule**: Detailed payment schedules
- **users**: User management data

## Security Features

- SSL encryption enabled automatically
- External access configured with proper authentication
- Firewall rules configured for port 5432
- Password-protected database access

## Troubleshooting

### If Power BI Cannot Connect

1. **Check PostgreSQL Service**:
   ```bash
   sudo systemctl status postgresql
   sudo systemctl start postgresql
   ```

2. **Verify Firewall**:
   ```bash
   sudo ufw status
   sudo ufw allow 5432/tcp
   ```

3. **Test Connection Locally**:
   ```bash
   psql -h localhost -p 5432 -U novellus_user -d novellus_loans
   ```

4. **Check External Connectivity**:
   ```bash
   telnet [YOUR_SERVER_IP] 5432
   ```

### SSL Certificate Issues

**Problem**: "The remote certificate is invalid according to the validation procedure"

**Solutions** (try in order):

#### Option 1: Disable SSL Validation
Use this connection string in Power BI:
```
Server=[YOUR_SERVER_IP];Database=novellus_loans;Port=5432;User Id=novellus_user;Password=novellus_secure_2025;SSL Mode=Disable;
```

#### Option 2: Trust Server Certificate
Use this connection string:
```
Server=[YOUR_SERVER_IP];Database=novellus_loans;Port=5432;User Id=novellus_user;Password=novellus_secure_2025;SSL Mode=Require;Trust Server Certificate=true;
```

#### Option 3: Generate Valid SSL Certificate
Run this command on your server:
```bash
sudo openssl req -new -x509 -days 365 -nodes -text -out server.crt -keyout server.key -subj "/CN=[YOUR_SERVER_IP]"
sudo chown postgres:postgres server.crt server.key
sudo chmod 600 server.key
sudo mv server.crt server.key /var/lib/postgresql/[VERSION]/main/
```

#### Option 4: Power BI Service with On-Premises Gateway
For Power BI Service, install the On-Premises Data Gateway and configure:
- **Server**: localhost (from gateway perspective)
- **Database**: novellus_loans  
- **Username**: novellus_user
- **Password**: novellus_secure_2025
- **SSL**: Disabled (internal connection)

## Reverting to Cloud Database

If you need to revert to cloud database:
1. Restore original .env: `cp .env.cloud.backup .env`
2. Restart application: `./start.sh`

## Files Modified by start.sh

- `.env` - Updated with on-premise database configuration
- `/etc/postgresql/*/main/postgresql.conf` - External access configuration
- `/etc/postgresql/*/main/pg_hba.conf` - Authentication rules
- Firewall rules - Port 5432 opened

## Next Steps

1. Run `./start.sh` to configure everything automatically
2. Note the Power BI connection details displayed
3. Test connection in Power BI Desktop
4. Import `loan_summary` and `payment_schedule` tables
5. Build your dashboards and reports

All configuration is handled automatically - no manual database setup required!