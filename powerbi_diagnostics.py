#!/usr/bin/env python3
"""
Power BI Diagnostics Tool
Comprehensive testing and diagnostic tool for Power BI refresh functionality
"""

import os
import sys
import logging
from powerbi_refresh import PowerBIRefresher

def run_infrastructure_tests():
    """Test the infrastructure components without requiring credentials"""
    print("=" * 60)
    print("Power BI Infrastructure Diagnostics")
    print("=" * 60)
    
    results = {
        'chromium_installed': False,
        'selenium_available': False,
        'webdriver_manager_available': False,
        'chrome_driver_compatible': False
    }
    
    # Test 1: Chromium Installation
    print("1. Testing Chromium installation...")
    try:
        import subprocess
        result = subprocess.run(['chromium', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            results['chromium_installed'] = True
            print(f"✓ Chromium installed: {result.stdout.strip()}")
        else:
            print("✗ Chromium not accessible")
    except Exception as e:
        print(f"✗ Chromium test failed: {str(e)}")
    
    # Test 2: Selenium Availability
    print("\n2. Testing Selenium availability...")
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        results['selenium_available'] = True
        print("✓ Selenium modules available")
    except ImportError as e:
        print(f"✗ Selenium import failed: {str(e)}")
    
    # Test 3: WebDriver Manager
    print("\n3. Testing WebDriver Manager...")
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        results['webdriver_manager_available'] = True
        print("✓ WebDriver Manager available")
    except ImportError as e:
        print(f"✗ WebDriver Manager import failed: {str(e)}")
    
    # Test 4: Chrome Driver Compatibility (if all previous tests pass)
    if all([results['chromium_installed'], results['selenium_available'], results['webdriver_manager_available']]):
        print("\n4. Testing Chrome driver compatibility...")
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            
            options = Options()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            
            # Try to find Chrome binary
            chrome_paths = [
                "/nix/store/zi4f80l169xlmivz8vja8wlphq74qqk0-chromium-125.0.6422.141/bin/chromium",
                "/usr/bin/chromium",
                "/usr/bin/chromium-browser"
            ]
            
            chrome_binary = None
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_binary = path
                    break
            
            if chrome_binary:
                options.binary_location = chrome_binary
                print(f"   Using Chrome binary: {chrome_binary}")
            
            # Try to initialize driver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.get("https://www.google.com")
            driver.quit()
            
            results['chrome_driver_compatible'] = True
            print("✓ Chrome driver working correctly")
            
        except Exception as e:
            print(f"✗ Chrome driver test failed: {str(e)}")
    else:
        print("\n4. Skipping Chrome driver test (prerequisites not met)")
    
    # Summary
    print("\n" + "=" * 60)
    print("Infrastructure Test Summary")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All infrastructure tests passed! Power BI refresh should work once credentials are provided.")
    else:
        print("⚠️  Some infrastructure issues detected. Please resolve before using Power BI refresh.")
        
    return results

def test_with_dummy_credentials():
    """Test Power BI setup with dummy credentials to validate driver initialization"""
    print("\n" + "=" * 60)
    print("Chrome Driver Test (No Login)")
    print("=" * 60)
    
    # Create refresher with dummy credentials to bypass credential check
    refresher = PowerBIRefresher(
        username="test@example.com",
        password="dummy_password",
        dataset_url="https://app.powerbi.com/test"
    )
    
    def notification_callback(notification):
        print(f"[{notification['level']}] {notification['message']}")
    
    refresher.add_notification_callback(notification_callback)
    
    print("Testing Chrome driver initialization (no actual login)...")
    driver_success = refresher.setup_driver()
    
    if driver_success:
        print("✓ Chrome driver initialized successfully")
        print("✓ Power BI automation infrastructure is ready")
        
        # Clean up
        if refresher.driver:
            refresher.driver.quit()
            print("✓ Driver cleaned up properly")
        
        return True
    else:
        print("✗ Chrome driver initialization failed")
        return False

if __name__ == "__main__":
    # Run infrastructure tests
    infra_results = run_infrastructure_tests()
    
    # If infrastructure is good, test with dummy credentials
    if all(infra_results.values()):
        dummy_test_success = test_with_dummy_credentials()
        
        if dummy_test_success:
            print("\n🎉 Power BI automation is ready to use!")
            print("\nTo start using Power BI refresh:")
            print("1. Go to the Power BI Configuration page")
            print("2. Enter your actual Power BI credentials")
            print("3. Click 'Test Connection' to verify")
            print("4. Use 'Start Refresh' or 'Schedule Refresh' as needed")
        else:
            print("\n❌ Power BI automation setup incomplete")
    else:
        print("\n❌ Infrastructure issues prevent Power BI automation")
        print("Please resolve the failed tests above.")