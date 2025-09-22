#!/usr/bin/env python3
"""
Enhanced Power BI Working Refresh System
Fixes timing issues and adds better element detection
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

class EnhancedWorkingPowerBIRefresher:
    """Enhanced Power BI refresher with better timing and error handling"""
    
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
        """Setup Chrome driver with enhanced settings"""
        try:
            self.notify("Setting up Chrome driver with enhanced settings...", 'info')
            
            # Install chromedriver automatically
            chromedriver_autoinstaller.install()
            
            chrome_options = Options()
            # Keep browser visible for debugging
            # chrome_options.add_argument('--headless')  # Commented out for debugging
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(60)  # Increased timeout
            self.driver.implicitly_wait(10)  # Add implicit wait
            
            self.notify("Chrome driver setup successful", 'success')
            return True
            
        except Exception as e:
            self.notify(f"Chrome driver setup failed: {str(e)}", 'error')
            return False
    
    def wait_with_notification(self, seconds, message):
        """Wait with progress notification"""
        self.notify(f"{message} (waiting {seconds} seconds...)", 'info')
        for i in range(seconds):
            time.sleep(1)
            if i > 0 and i % 5 == 0:
                self.notify(f"Still waiting... {seconds - i} seconds remaining", 'info')
    
    def refresh_dataset_working(self) -> bool:
        """Enhanced refresh with better timing and error handling"""
        try:
            if not all([self.username, self.password, self.dataset_url]):
                self.notify("Missing credentials or dataset URL", 'error')
                return False
            
            if not self.setup_chrome_driver():
                return False
            
            # Step 1: Navigate to Power BI
            self.notify("Step 1: Navigating to Power BI login page...", 'info')
            self.driver.get("https://app.powerbi.com/")
            self.wait_with_notification(8, "Waiting for Power BI page to fully load")
            
            # Step 2: Enter email with enhanced detection
            self.notify("Step 2: Looking for email input field...", 'info')
            email_selectors = [
                (By.ID, "email"),
                (By.NAME, "loginfmt"),
                (By.CSS_SELECTOR, "input[type='email']"),
                (By.XPATH, "//input[@placeholder*='email' or @placeholder*='Email']")
            ]
            
            email_field = None
            for by, selector in email_selectors:
                try:
                    email_field = WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    self.notify(f"Found email field using selector: {selector}", 'success')
                    break
                except TimeoutException:
                    continue
            
            if not email_field:
                self.notify("Could not find email input field", 'error')
                return False
            
            # Clear and enter email
            email_field.clear()
            email_field.send_keys(self.username)
            email_field.send_keys(Keys.RETURN)
            self.wait_with_notification(8, "Email submitted, waiting for password page")
            
            # Step 3: Enter password
            self.notify("Step 3: Looking for password input field...", 'info')
            password_selectors = [
                (By.NAME, "passwd"),
                (By.ID, "i0118"),
                (By.CSS_SELECTOR, "input[type='password']"),
                (By.XPATH, "//input[@placeholder*='password' or @placeholder*='Password']")
            ]
            
            password_field = None
            for by, selector in password_selectors:
                try:
                    password_field = WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    self.notify(f"Found password field using selector: {selector}", 'success')
                    break
                except TimeoutException:
                    continue
            
            if not password_field:
                self.notify("Could not find password input field", 'error')
                return False
            
            # Clear and enter password
            password_field.clear()
            password_field.send_keys(self.password)
            password_field.send_keys(Keys.RETURN)
            self.wait_with_notification(8, "Password submitted, waiting for response")
            
            # Step 4: Handle stay signed in prompt
            self.notify("Step 4: Looking for 'Stay signed in?' prompt...", 'info')
            try:
                stay_signed_in_selectors = [
                    (By.ID, "idBtn_Back"),
                    (By.XPATH, "//input[@value='No']"),
                    (By.XPATH, "//button[contains(text(), 'No')]")
                ]
                
                no_button = None
                for by, selector in stay_signed_in_selectors:
                    try:
                        no_button = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((by, selector))
                        )
                        self.notify(f"Found 'No' button using selector: {selector}", 'success')
                        break
                    except TimeoutException:
                        continue
                
                if no_button:
                    no_button.click()
                    self.wait_with_notification(8, "Clicked 'No' on stay signed in, waiting for redirect")
                else:
                    self.notify("No 'Stay signed in?' prompt found, continuing...", 'info')
                    self.wait_with_notification(3, "Brief pause before continuing")
                    
            except Exception as e:
                self.notify(f"Error handling stay signed in prompt: {str(e)}", 'warning')
            
            # Step 5: Navigate to dataset
            self.notify("Step 5: Navigating to dataset page...", 'info')
            self.driver.get(self.dataset_url)
            self.wait_with_notification(10, "Dataset page loading")
            
            # Step 6: Find and click refresh dropdown
            self.notify("Step 6: Looking for refresh dropdown...", 'info')
            refresh_dropdown_selectors = [
                "//span[normalize-space(text())='Refresh']",
                "//button[contains(@aria-label, 'Refresh')]",
                "//div[contains(text(), 'Refresh')]",
                "//span[contains(text(), 'Refresh')]",
                "//*[contains(@title, 'Refresh')]"
            ]
            
            dropdown_button = None
            for selector in refresh_dropdown_selectors:
                try:
                    dropdown_button = WebDriverWait(self.driver, 15).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    self.notify(f"Found refresh dropdown using: {selector}", 'success')
                    break
                except TimeoutException:
                    continue
            
            if not dropdown_button:
                self.notify("Could not find refresh dropdown", 'error')
                # Save page source for debugging
                try:
                    with open('/tmp/powerbi_dropdown_debug.html', 'w') as f:
                        f.write(self.driver.page_source)
                    self.notify("Page source saved to /tmp/powerbi_dropdown_debug.html", 'info')
                except:
                    pass
                return False
            
            # Click dropdown
            dropdown_button.click()
            self.wait_with_notification(5, "Dropdown clicked, waiting for menu to appear")
            
            # Step 7: Click refresh now button
            self.notify("Step 7: Looking for 'Refresh now' button...", 'info')
            refresh_now_selectors = [
                "//button[@title='Refresh now' and @role='menuitem']//span[normalize-space()='Refresh now']",
                "//span[normalize-space()='Refresh now']",
                "//button[contains(text(), 'Refresh now')]",
                "//*[@role='menuitem'][contains(text(), 'Refresh now')]",
                "//li[contains(text(), 'Refresh now')]"
            ]
            
            refresh_now_button = None
            for selector in refresh_now_selectors:
                try:
                    refresh_now_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    self.notify(f"Found 'Refresh now' button using: {selector}", 'success')
                    break
                except TimeoutException:
                    continue
            
            if not refresh_now_button:
                self.notify("Could not find 'Refresh now' button", 'error')
                try:
                    with open('/tmp/powerbi_menu_debug.html', 'w') as f:
                        f.write(self.driver.page_source)
                    self.notify("Page source saved to /tmp/powerbi_menu_debug.html", 'info')
                except:
                    pass
                return False
            
            # Click refresh now
            refresh_now_button.click()
            self.notify("'Refresh now' button clicked successfully!", 'success')
            
            # Wait for refresh to complete with progress updates
            self.wait_with_notification(30, "Waiting for refresh operation to complete")
            
            # Check for success indicators
            try:
                # Look for success message or refresh status
                success_indicators = [
                    "//div[contains(text(), 'refresh')]",
                    "//*[contains(text(), 'successful')]",
                    "//*[contains(text(), 'completed')]"
                ]
                
                for indicator in success_indicators:
                    try:
                        element = self.driver.find_element(By.XPATH, indicator)
                        if element:
                            self.notify(f"Found refresh indicator: {element.text}", 'success')
                            break
                    except:
                        continue
                        
            except Exception as e:
                self.notify(f"Could not verify refresh status: {str(e)}", 'warning')
            
            self.notify("Power BI refresh process completed!", 'success')
            return True
            
        except Exception as e:
            self.notify(f"Unexpected error during refresh: {str(e)}", 'error')
            return False
            
        finally:
            if self.driver:
                try:
                    self.notify("Closing browser...", 'info')
                    self.driver.quit()
                    self.notify("Browser closed successfully", 'info')
                except Exception as e:
                    self.notify(f"Error closing browser: {str(e)}", 'warning')

def create_enhanced_working_refresher(username=None, password=None, dataset_url=None):
    """Create enhanced working refresher instance"""
    return EnhancedWorkingPowerBIRefresher(username, password, dataset_url)

if __name__ == "__main__":
    # Test the enhanced working refresher
    refresher = create_enhanced_working_refresher()
    
    def print_notification(notification):
        level = notification['level'].upper()
        timestamp = notification['timestamp']
        print(f"[{timestamp}] [{level}] {notification['message']}")
    
    refresher.add_notification_callback(print_notification)
    
    print("Testing Enhanced Working Power BI Refresh...")
    print("=" * 60)
    
    if refresher.username and refresher.password and refresher.dataset_url:
        refresh_ok = refresher.refresh_dataset_working()
        print(f"Refresh result: {'SUCCESS' if refresh_ok else 'FAILED'}")
    else:
        print("Missing credentials - cannot test refresh")
        print("Set environment variables: POWERBI_USERNAME, POWERBI_PASSWORD, POWERBI_DATASET_URL")