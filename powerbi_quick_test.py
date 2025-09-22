#!/usr/bin/env python3
"""
Quick Power BI Test - Test with environment variables if available
"""

import os
from powerbi_refresh import PowerBIRefresher

def quick_test():
    print("Quick Power BI Test")
    print("=" * 40)
    
    # Check for environment variables
    username = os.environ.get('POWERBI_USERNAME')
    password = os.environ.get('POWERBI_PASSWORD') 
    dataset_url = os.environ.get('POWERBI_DATASET_URL')
    
    if username and password and dataset_url:
        print("✓ Environment variables found")
        print(f"Username: {username}")
        print(f"Dataset URL: {dataset_url[:50]}...")
        
        refresher = PowerBIRefresher()
        
        def notification_callback(notification):
            print(f"[{notification['level']}] {notification['message']}")
        
        refresher.add_notification_callback(notification_callback)
        
        print("\nTesting full Power BI refresh...")
        try:
            success = refresher.refresh_dataset()
            if success:
                print("✓ Power BI refresh completed successfully!")
            else:
                print("✗ Power BI refresh failed")
        except Exception as e:
            print(f"✗ Error during refresh: {str(e)}")
    else:
        print("⚠ Environment variables not set")
        print("Using dummy credentials to test infrastructure...")
        
        refresher = PowerBIRefresher(
            username="test@example.com",
            password="dummy_password", 
            dataset_url="https://app.powerbi.com/test"
        )
        
        def notification_callback(notification):
            print(f"[{notification['level']}] {notification['message']}")
        
        refresher.add_notification_callback(notification_callback)
        
        print("\nTesting Chrome driver setup...")
        try:
            success = refresher.setup_driver()
            if success:
                print("✓ Chrome driver setup successful!")
                print("✓ Power BI infrastructure ready")
                if refresher.driver:
                    refresher.driver.quit()
            else:
                print("✗ Chrome driver setup failed")
        except Exception as e:
            print(f"✗ Error during setup: {str(e)}")

if __name__ == "__main__":
    quick_test()