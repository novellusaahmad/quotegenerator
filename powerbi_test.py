#!/usr/bin/env python3
"""
Power BI Refresh Test Script
Test Power BI automation functionality and Chrome driver setup
"""

import os
import sys
import logging
from powerbi_refresh import PowerBIRefresher

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_powerbi_refresh():
    """Test Power BI refresh functionality"""
    print("=" * 60)
    print("Power BI Refresh Test")
    print("=" * 60)
    
    # Test notification callback
    def notification_callback(notification):
        print(f"[{notification['level']}] {notification['message']}")
    
    # Initialize refresher
    refresher = PowerBIRefresher()
    refresher.add_notification_callback(notification_callback)
    
    print("1. Testing Chrome driver setup...")
    driver_success = refresher.setup_driver()
    
    if driver_success:
        print("✓ Chrome driver setup successful")
        
        # Check environment variables
        print("\n2. Checking Power BI configuration...")
        print(f"Username configured: {'Yes' if refresher.username else 'No'}")
        print(f"Password configured: {'Yes' if refresher.password else 'No'}")
        print(f"Dataset URL configured: {'Yes' if refresher.dataset_url else 'No'}")
        
        if refresher.username and refresher.password and refresher.dataset_url:
            print("\n3. Testing Power BI login...")
            try:
                login_success = refresher.login_to_powerbi()
                if login_success:
                    print("✓ Power BI login successful")
                    
                    print("\n4. Testing dataset refresh...")
                    refresh_success = refresher.refresh_dataset()
                    if refresh_success:
                        print("✓ Dataset refresh successful")
                    else:
                        print("✗ Dataset refresh failed")
                else:
                    print("✗ Power BI login failed")
            except Exception as e:
                print(f"✗ Login test error: {str(e)}")
        else:
            print("⚠ Power BI credentials not configured - skipping login test")
            print("\nTo configure Power BI credentials, set these environment variables:")
            print("- POWERBI_USERNAME: Your Power BI username/email")
            print("- POWERBI_PASSWORD: Your Power BI password")
            print("- POWERBI_DATASET_URL: URL to your Power BI dataset")
        
        # Clean up
        if refresher.driver:
            refresher.driver.quit()
    else:
        print("✗ Chrome driver setup failed")
        print("\nTroubleshooting steps:")
        print("1. Ensure Chromium is installed: chromium --version")
        print("2. Check if Selenium is installed: pip list | grep selenium")
        print("3. Verify webdriver-manager: pip list | grep webdriver-manager")
    
    print("\n" + "=" * 60)
    print("Test completed")
    print("=" * 60)

if __name__ == "__main__":
    test_powerbi_refresh()