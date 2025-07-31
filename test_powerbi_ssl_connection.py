#!/usr/bin/env python3
"""
Test script to diagnose Power BI SSL connection issues
"""

import os
import socket
import psycopg2

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def print_result(text, success=True):
    icon = "✅" if success else "❌"
    print(f"{icon} {text}")

def get_server_ip():
    """Get the server's IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "localhost"

def test_ssl_connection():
    """Test PostgreSQL SSL connection"""
    print_header("Power BI SSL Connection Diagnostic")
    
    # Get server IP
    server_ip = get_server_ip()
    print(f"🔍 Server IP: {server_ip}")
    
    # Database connection parameters
    db_params = {
        'host': server_ip,
        'port': 5432,
        'database': 'novellus_loans',
        'user': 'novellus_user',
        'password': 'novellus_secure_2025'
    }
    
    print_header("Testing Connection Methods")
    
    # Test 1: SSL Disabled (recommended for Power BI Service)
    print("🔧 Testing SSL Disabled connection...")
    try:
        conn = psycopg2.connect(**db_params, sslmode='disable')
        cursor = conn.cursor()
        cursor.execute("SELECT current_database(), current_user;")
        db_name, user = cursor.fetchone()
        cursor.close()
        conn.close()
        print_result(f"SSL Disabled: Connected to {db_name} as {user}")
        ssl_disabled_works = True
    except Exception as e:
        print_result(f"SSL Disabled failed: {e}", False)
        ssl_disabled_works = False
    
    # Test 2: SSL Required with Trust Certificate
    print("\n🔧 Testing SSL Required with Trust Certificate...")
    try:
        conn = psycopg2.connect(**db_params, sslmode='require')
        cursor = conn.cursor()
        cursor.execute("SELECT current_database(), current_user;")
        db_name, user = cursor.fetchone()
        cursor.close()
        conn.close()
        print_result(f"SSL Required: Connected to {db_name} as {user}")
        ssl_required_works = True
    except Exception as e:
        print_result(f"SSL Required failed: {e}", False)
        ssl_required_works = False
    
    # Generate connection strings
    print_header("Power BI Connection Strings")
    
    if ssl_disabled_works:
        print("🎯 RECOMMENDED: Use SSL Disabled for Power BI Service")
        print(f"Connection String:")
        print(f"Server={server_ip};Database=novellus_loans;Port=5432;User Id=novellus_user;Password=novellus_secure_2025;SSL Mode=Disable;")
        print()
    
    if ssl_required_works:
        print("🔒 Alternative: SSL Enabled with Trust Certificate")
        print(f"Connection String:")
        print(f"Server={server_ip};Database=novellus_loans;Port=5432;User Id=novellus_user;Password=novellus_secure_2025;SSL Mode=Require;Trust Server Certificate=true;")
        print()
    
    # Recommendations
    print_header("Recommendations")
    
    if ssl_disabled_works:
        print_result("✅ SOLUTION: Use SSL Mode=Disable connection string in Power BI")
        print("📋 This resolves the 'remote certificate is invalid' error")
        print("🔧 Steps:")
        print("   1. In Power BI, use the SSL Disabled connection string above")
        print("   2. Or in connection settings, add: SSL Mode=Disable;")
    else:
        print_result("❌ Database connection issues detected", False)
        print("🔧 Troubleshooting steps:")
        print("   1. Ensure PostgreSQL is running: sudo systemctl status postgresql")
        print("   2. Check firewall: sudo ufw status")
        print("   3. Verify pg_hba.conf allows connections")
    
    if not ssl_disabled_works and not ssl_required_works:
        print("\n🚨 Neither SSL mode works - check basic connectivity:")
        print(f"   telnet {server_ip} 5432")
    
    # Gateway recommendation
    print_header("Production Recommendation")
    print("🏢 For production Power BI Service connection:")
    print("   1. Install On-Premises Data Gateway on this server")
    print("   2. Configure gateway with localhost connection (no SSL issues)")
    print("   3. Connect Power BI Service through the gateway")
    print("   4. This provides secure connection without certificate problems")

if __name__ == "__main__":
    test_ssl_connection()