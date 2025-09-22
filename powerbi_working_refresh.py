#!/usr/bin/env python3
"""
Power BI Working Refresh System
Using the exact working code provided by user
"""

import os
import time
import logging
from datetime import datetime
from typing import Optional, Dict, Any

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
    from selenium.common.exceptions import TimeoutException, WebDriverException
    import chromedriver_autoinstaller
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

logger = logging.getLogger(__name__)

class WorkingPowerBIRefresher:
    """Power BI refresher using the exact working code provided by user"""
    
    def __init__(self, username=None, password=None, dataset_url=None):
        self.username = username or os.environ.get('POWERBI_USERNAME')
        self.password = password or os.environ.get('POWERBI_PASSWORD')
        self.dataset_url = dataset_url or os.environ.get('POWERBI_DATASET_URL')
        self.driver = None
        self.notification_callbacks = []
        
    def add_notification_callback(self, callback):
        """Add notification callback"""
        self.notification_callbacks.append(callback)
        
    def notify(self, message: str, level: str = 'info'):
        """Send notification to callbacks"""
        notification = {
            'message': message,
            'level': level,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Power BI Notification: {message}")
        
        for callback in self.notification_callbacks:
            try:
                callback(notification)
            except Exception as e:
                logger.error(f"Notification callback error: {e}")
    
    def setup_chrome_driver(self) -> bool:
        """Setup Chrome driver with optimized settings"""
        try:
            self.notify("Setting up Chrome driver...", 'info')
            
            # Install chromedriver automatically
            chromedriver_autoinstaller.install()
            
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--remote-debugging-port=9222')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            
            self.notify("Chrome driver setup successful", 'success')
            return True
            
        except Exception as e:
            self.notify(f"Chrome driver setup failed: {str(e)}", 'error')
            return False
    
    def refresh_dataset_working(self) -> bool:
        """Refresh dataset using the exact working code provided by user with proper timing"""
        try:
            if not all([self.username, self.password, self.dataset_url]):
                self.notify("Missing credentials or dataset URL", 'error')
                return False
            
            if not self.setup_chrome_driver():
                return False
            
            # Step 1: Go to Power BI login
            self.notify("Step 1: Navigating to Power BI login...", 'info')
            self.driver.get("https://app.powerbi.com/")
            self.notify("Waiting 5 seconds for page to load...", 'info')
            time.sleep(5)  # Critical wait time
            
            # Step 2: Enter email
            self.notify("Step 2: Looking for email field...", 'info')
            try:
                email_field = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.ID, "email"))
                )
                self.notify("Found email field, entering username...", 'info')
                email_field.send_keys(self.username + Keys.RETURN)
                self.notify("Email submitted, waiting 5 seconds...", 'info')
                time.sleep(5)  # Critical wait time
            except TimeoutException:
                self.notify("Email field 'email' not found, trying alternative selector...", 'warning')
                try:
                    email_field = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.NAME, "loginfmt"))
                    )
                    email_field.send_keys(self.username)
                    next_btn = self.driver.find_element(By.ID, "idSIButton9")
                    next_btn.click()
                    time.sleep(3)
                except Exception as e:
                    self.notify(f"Could not find email field: {str(e)}", 'error')
                    return False
            
            # Step 3: Enter password
            self.notify("Step 3: Looking for password field...", 'info')
            try:
                password_field = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.NAME, "passwd"))
                )
                self.notify("Found password field, entering password...", 'info')
                password_field.send_keys(self.password + Keys.RETURN)
                self.notify("Password submitted, waiting 5 seconds...", 'info')
                time.sleep(5)  # Critical wait time
            except TimeoutException as e:
                self.notify(f"Password field not found: {str(e)}", 'error')
                return False
            
            # Step 4: Handle "Stay signed in?" prompt
            self.notify("Step 4: Looking for 'Stay signed in?' prompt...", 'info')
            try:
                stay_signed_in_no = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.ID, "idBtn_Back"))
                )
                self.notify("Found 'Stay signed in?' prompt, clicking No...", 'info')
                stay_signed_in_no.click()
                
                # CRITICAL: Wait time before navigating as specified in working code
                self.notify("Waiting 5 seconds before proceeding to dataset...", 'info')
                time.sleep(5)  # Critical wait time as specified
            except TimeoutException:
                self.notify("No 'Stay signed in?' prompt found, continuing...", 'info')
                time.sleep(2)
            
            # Step 5: Go to dataset settings page
            self.notify(f"Step 5: Navigating to dataset URL...", 'info')
            self.driver.get(self.dataset_url)
            self.notify("Dataset page loaded, waiting 3 seconds...", 'info')
            time.sleep(3)  # Wait for page to load
            
            # Step 6: Click the refresh dropdown
            self.notify("Step 6: Looking for refresh dropdown...", 'info')
            try:
                dropdown_button = WebDriverWait(self.driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[normalize-space(text())='Refresh']"))
                )
                self.notify("Found refresh dropdown, clicking...", 'success')
                dropdown_button.click()
                self.notify("Dropdown clicked, waiting 3 seconds...", 'info')
                time.sleep(3)  # Wait for dropdown to open
            except TimeoutException as e:
                self.notify(f"Refresh dropdown not found: {str(e)}", 'error')
                # Save page for debugging
                try:
                    with open('/tmp/powerbi_debug.html', 'w') as f:
                        f.write(self.driver.page_source)
                    self.notify("Page source saved for debugging", 'info')
                except:
                    pass
                return False
            
            # Step 7: Click the "Refresh now" button
            self.notify("Step 7: Looking for 'Refresh now' button...", 'info')
            try:
                refresh_button = WebDriverWait(self.driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@title='Refresh now' and @role='menuitem']//span[normalize-space()='Refresh now']"))
                )
                self.notify("Found 'Refresh now' button, clicking...", 'success')
                refresh_button.click()
                self.notify("Refresh button clicked successfully!", 'success')
                
                # CRITICAL: Wait for refresh operation to start/complete
                self.notify("Waiting 20 seconds for refresh operation...", 'info')
                time.sleep(20)  # Critical wait time as specified
                
                return True
                
            except TimeoutException as e:
                self.notify(f"'Refresh now' button not found: {str(e)}", 'error')
                return False
            
        except Exception as e:
            self.notify(f"Unexpected error during refresh: {str(e)}", 'error')
            return False
            
        finally:
            if self.driver:
                try:
                    self.notify("Closing Chrome driver...", 'info')
                    self.driver.quit()
                    self.notify("Chrome driver closed successfully", 'info')
                except Exception as e:
                    self.notify(f"Error closing driver: {str(e)}", 'warning')
    
    def test_connection(self) -> bool:
        """Test Power BI connection"""
        try:
            if not all([self.username, self.password, self.dataset_url]):
                self.notify("Missing credentials for connection test", 'error')
                return False
            
            self.notify("Testing Power BI connection...", 'info')
            
            if not self.setup_chrome_driver():
                return False
            
            # Just test login
            self.driver.get("https://app.powerbi.com/")
            time.sleep(5)
            
            # Check if login page loads
            try:
                email_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "email"))
                )
                self.notify("Power BI login page accessible", 'success')
                return True
            except TimeoutException:
                # Try alternative selector
                try:
                    email_field = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.NAME, "loginfmt"))
                    )
                    self.notify("Power BI login page accessible (alternative)", 'success')
                    return True
                except TimeoutException:
                    self.notify("Could not access Power BI login page", 'error')
                    return False
                    
        except Exception as e:
            self.notify(f"Connection test failed: {str(e)}", 'error')
            return False
        finally:
            if self.driver:
                self.driver.quit()

def create_working_refresher(username=None, password=None, dataset_url=None) -> WorkingPowerBIRefresher:
    """Create working refresher instance"""
    return WorkingPowerBIRefresher(username, password, dataset_url)

if __name__ == "__main__":
    # Test the working refresher
    refresher = create_working_refresher()
    
    def print_notification(notification):
        level = notification['level'].upper()
        print(f"[{level}] {notification['message']}")
    
    refresher.add_notification_callback(print_notification)
    
    print("Testing Working Power BI Refresh...")
    print("=" * 50)
    
    # Test connection first
    connection_ok = refresher.test_connection()
    print(f"Connection test: {'PASSED' if connection_ok else 'FAILED'}")
    
    if connection_ok:
        # Test actual refresh (only if credentials are available)
        if refresher.username and refresher.password and refresher.dataset_url:
            refresh_ok = refresher.refresh_dataset_working()
            print(f"Refresh test: {'PASSED' if refresh_ok else 'FAILED'}")
        else:
            print("Skipping refresh test - missing credentials")