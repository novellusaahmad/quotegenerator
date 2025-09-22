#!/usr/bin/env python3
"""
Enhanced Power BI Refresh System
- Better refresh button detection
- Improved error handling
- Enhanced notification system
"""

import os
import logging
import time
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

logger = logging.getLogger(__name__)

class EnhancedPowerBIRefresher:
    """Enhanced Power BI refresher with improved element detection"""
    
    def __init__(self, username: str = None, password: str = None, dataset_url: str = None):
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
            'timestamp': time.time()
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
            
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--remote-debugging-port=9222')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-images')
            chrome_options.add_argument('--disable-javascript')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # Import and install chromedriver
            import chromedriver_autoinstaller
            chromedriver_autoinstaller.install()
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            
            self.notify("Chrome driver setup successful", 'success')
            return True
            
        except Exception as e:
            self.notify(f"Chrome driver setup failed: {str(e)}", 'error')
            return False
    
    def login_to_powerbi(self) -> bool:
        """Enhanced Power BI login process"""
        try:
            self.notify("Navigating to Power BI login page...", 'info')
            self.driver.get('https://app.powerbi.com/')
            
            wait = WebDriverWait(self.driver, 20)
            
            # Wait for login page to load
            time.sleep(3)
            
            # Look for email input field
            email_selectors = [
                "input[type='email']",
                "input[name='loginfmt']",
                "#i0116",
                "input[placeholder*='email']",
                "input[aria-label*='email']"
            ]
            
            email_input = None
            for selector in email_selectors:
                try:
                    email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    break
                except TimeoutException:
                    continue
            
            if not email_input:
                self.notify("Could not find email input field", 'error')
                return False
            
            self.notify("Entering username...", 'info')
            email_input.clear()
            email_input.send_keys(self.username)
            
            # Click next button
            next_selectors = [
                "input[type='submit']",
                "input[value='Next']",
                "#idSIButton9",
                "button[type='submit']"
            ]
            
            for selector in next_selectors:
                try:
                    next_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    next_btn.click()
                    break
                except NoSuchElementException:
                    continue
            
            time.sleep(3)
            
            # Look for password input field
            password_selectors = [
                "input[type='password']",
                "input[name='passwd']",
                "#i0118",
                "input[placeholder*='password']",
                "input[aria-label*='password']"
            ]
            
            password_input = None
            for selector in password_selectors:
                try:
                    password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    break
                except TimeoutException:
                    continue
            
            if not password_input:
                self.notify("Could not find password input field", 'error')
                return False
            
            self.notify("Entering password...", 'info')
            password_input.clear()
            password_input.send_keys(self.password)
            
            # Click sign in button
            signin_selectors = [
                "input[type='submit']",
                "input[value='Sign in']",
                "#idSIButton9",
                "button[type='submit']"
            ]
            
            for selector in signin_selectors:
                try:
                    signin_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    signin_btn.click()
                    break
                except NoSuchElementElement:
                    continue
            
            self.notify("Login submitted, waiting for redirect...", 'info')
            time.sleep(5)
            
            return True
            
        except Exception as e:
            self.notify(f"Login failed: {str(e)}", 'error')
            return False
    
    def find_and_click_refresh(self) -> bool:
        """Enhanced refresh button detection and clicking"""
        try:
            self.notify("Looking for refresh button with enhanced detection...", 'info')
            
            wait = WebDriverWait(self.driver, 10)
            
            # Enhanced refresh button selectors for 2024/2025 Power BI interface
            refresh_selectors = [
                # Modern Power BI interface selectors
                "button[aria-label*='Refresh']",
                "button[title*='Refresh']",
                "button[data-testid*='refresh']",
                "div[class*='commandbar'] button[aria-label*='Refresh']",
                "div[class*='toolbar'] button[title*='Refresh']",
                
                # Fluent UI selectors
                "button[class*='ms-Button'] span:contains('Refresh')",
                "button[class*='pbi-button'] span:contains('Refresh')",
                
                # XPath selectors
                "//button[contains(@aria-label, 'Refresh')]",
                "//button[@title='Refresh']",
                "//button[contains(@class, 'refresh')]",
                "//span[normalize-space(text())='Refresh']",
                "//button[contains(text(), 'Refresh')]",
                "//div[contains(@class, 'commandbar')]//button[contains(@aria-label, 'Refresh')]",
                "//div[contains(@class, 'toolbar')]//button[contains(@title, 'Refresh')]",
                "//button[contains(@class, 'ms-Button')]//span[contains(text(), 'Refresh')]",
                "//button[contains(@class, 'pbi-button')]//span[contains(text(), 'Refresh')]",
                
                # Generic selectors
                "//*[@data-testid='refresh-button']",
                "//*[contains(@class, 'refreshButton')]",
                "//button[contains(@class, 'dataset-refresh')]",
                "//a[contains(@href, 'refresh')]"
            ]
            
            refresh_button = None
            for i, selector in enumerate(refresh_selectors):
                try:
                    self.notify(f"Trying selector {i+1}/{len(refresh_selectors)}: {selector[:50]}...", 'info')
                    
                    if selector.startswith('//'):
                        # XPath selector
                        refresh_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    else:
                        # CSS selector
                        refresh_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    
                    self.notify(f"Found refresh button with selector: {selector}", 'success')
                    break
                    
                except TimeoutException:
                    continue
                except Exception as e:
                    self.notify(f"Error with selector {selector}: {str(e)}", 'warning')
                    continue
            
            if not refresh_button:
                self.notify("Could not find refresh button with any selector", 'error')
                # Save page source for debugging
                with open('/tmp/powerbi_page_source.html', 'w') as f:
                    f.write(self.driver.page_source)
                self.notify("Page source saved to /tmp/powerbi_page_source.html for debugging", 'info')
                return False
            
            self.notify("Clicking refresh button...", 'info')
            refresh_button.click()
            
            self.notify("Refresh button clicked successfully!", 'success')
            time.sleep(3)  # Wait for refresh to start
            
            return True
            
        except Exception as e:
            self.notify(f"Error finding/clicking refresh button: {str(e)}", 'error')
            return False
    
    def refresh_dataset(self) -> bool:
        """Main refresh process"""
        try:
            if not all([self.username, self.password, self.dataset_url]):
                self.notify("Missing credentials or dataset URL", 'error')
                return False
            
            # Setup Chrome driver
            if not self.setup_chrome_driver():
                return False
            
            # Login to Power BI
            if not self.login_to_powerbi():
                return False
            
            # Navigate to dataset
            self.notify(f"Navigating to dataset: {self.dataset_url}", 'info')
            self.driver.get(self.dataset_url)
            time.sleep(5)
            
            # Find and click refresh
            if not self.find_and_click_refresh():
                return False
            
            self.notify("Dataset refresh initiated successfully!", 'success')
            return True
            
        except Exception as e:
            self.notify(f"Dataset refresh failed: {str(e)}", 'error')
            return False
        finally:
            if self.driver:
                self.driver.quit()
                self.notify("Chrome driver closed", 'info')

def create_enhanced_refresher(username=None, password=None, dataset_url=None) -> EnhancedPowerBIRefresher:
    """Create enhanced refresher instance"""
    return EnhancedPowerBIRefresher(username, password, dataset_url)

if __name__ == "__main__":
    refresher = create_enhanced_refresher()
    
    def print_notification(notification):
        level = notification['level'].upper()
        print(f"[{level}] {notification['message']}")
    
    refresher.add_notification_callback(print_notification)
    
    print("Testing Enhanced Power BI Refresh...")
    print("=" * 50)
    
    success = refresher.refresh_dataset()
    print(f"Refresh success: {success}")