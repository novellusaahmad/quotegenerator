#!/usr/bin/env python3
"""
Power BI Refresh Automation
Novellus Loan Management System

Headless Power BI dataset refresh with notification system
"""

import os
import time
import logging
import asyncio
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
    from selenium.common.exceptions import TimeoutException, WebDriverException
    from selenium.webdriver.chrome.service import Service
    import chromedriver_autoinstaller
    SELENIUM_AVAILABLE = True
except ImportError as e:
    SELENIUM_AVAILABLE = False
    webdriver = None
    By = None
    Options = None
    WebDriverWait = None
    EC = None
    Keys = None
    TimeoutException = None
    WebDriverException = None
    Service = None
    chromedriver_autoinstaller = None
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('powerbi_refresh.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PowerBIRefresher:
    def __init__(self, username=None, password=None, dataset_url=None):
        self.username = username or os.environ.get('POWERBI_USERNAME')
        self.password = password or os.environ.get('POWERBI_PASSWORD')
        self.dataset_url = dataset_url or os.environ.get('POWERBI_DATASET_URL')
        self.driver = None
        self.notification_callbacks = []
        
    def add_notification_callback(self, callback):
        """Add a callback function for notifications"""
        self.notification_callbacks.append(callback)
        
    def notify(self, message, level="INFO"):
        """Send notification to all registered callbacks"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        notification = {
            "timestamp": timestamp,
            "level": level,
            "message": message
        }
        
        logger.info(f"Notification: {message}")
        
        for callback in self.notification_callbacks:
            try:
                callback(notification)
            except Exception as e:
                logger.error(f"Notification callback failed: {str(e)}")
    
    def setup_driver(self):
        """Set up headless Chrome driver with enhanced error handling"""
        if not SELENIUM_AVAILABLE:
            error_msg = "Selenium not available - Power BI refresh functionality disabled"
            logger.error(error_msg)
            self.notify(error_msg, "ERROR")
            return False
            
        # Check if credentials are available
        if not self.username or not self.password:
            error_msg = "Power BI credentials not configured. Please set POWERBI_USERNAME and POWERBI_PASSWORD environment variables."
            logger.error(error_msg)
            self.notify(error_msg, "ERROR")
            return False
            
        if not self.dataset_url:
            error_msg = "Power BI dataset URL not configured. Please set POWERBI_DATASET_URL environment variable."
            logger.error(error_msg)
            self.notify(error_msg, "ERROR")
            return False
            
        try:
            logger.info("Setting up Chrome driver for Power BI automation...")
            self.notify("Initializing Chrome driver for Power BI automation")
            
            options = Options()
            # Enhanced Chrome options for Replit environment
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-cache")
            options.add_argument("--incognito")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-features=VizDisplayCompositor")
            options.add_argument("--remote-debugging-port=9222")
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Try multiple Chrome/Chromium binaries
            chrome_paths = [
                "/nix/store/zi4f80l169xlmivz8vja8wlphq74qqk0-chromium-125.0.6422.141/bin/chromium",
                "/usr/bin/chromium",
                "/usr/bin/chromium-browser", 
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable"
            ]
            
            chrome_binary = None
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_binary = path
                    break
            
            if chrome_binary:
                options.binary_location = chrome_binary
                logger.info(f"Using Chrome binary: {chrome_binary}")
            
            # Use chromedriver-autoinstaller for automatic version matching
            try:
                # Auto-install compatible ChromeDriver
                chromedriver_autoinstaller.install()
                service = Service()
                logger.info("ChromeDriver auto-installed successfully")
            except Exception as install_error:
                logger.warning(f"ChromeDriver auto-install failed: {install_error}")
                # Fallback to system chromedriver
                service = Service()
            
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.delete_all_cookies()
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            logger.info("Chrome driver initialized successfully")
            self.notify("Chrome driver ready for Power BI automation", "SUCCESS")
            return True
            
        except Exception as e:
            error_msg = f"Failed to initialize Chrome driver: {str(e)}"
            logger.error(error_msg)
            self.notify(error_msg, "ERROR")
            
            # Additional troubleshooting information
            if "chrome" in str(e).lower():
                self.notify("Chrome browser may not be installed or accessible", "WARNING")
            if "permission" in str(e).lower():
                self.notify("Permission denied - check file system permissions", "WARNING")
            if "127" in str(e):
                self.notify("Chrome binary may be incompatible with current system", "WARNING")
                
            return False
    
    def login_to_powerbi(self):
        """Login to Power BI with enhanced error handling"""
        if not self.driver:
            error_msg = "Chrome driver not initialized"
            logger.error(error_msg)
            self.notify(error_msg, "ERROR")
            return False
            
        try:
            self.notify("Starting Power BI login process")
            logger.info("Navigating to Power BI login page")
            
            # Navigate to Power BI
            self.driver.get("https://app.powerbi.com/")
            time.sleep(5)
            
            # Enter email
            email_field = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            email_field.send_keys(self.username + Keys.RETURN)
            time.sleep(3)
            
            # Enter password
            password_field = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.NAME, "passwd"))
            )
            password_field.send_keys(self.password + Keys.RETURN)
            time.sleep(3)
            
            # Handle "Stay signed in?" prompt
            try:
                stay_signed_in = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "idBtn_Back"))
                )
                stay_signed_in.click()
                time.sleep(3)
            except TimeoutException:
                logger.info("No 'Stay signed in' prompt found")
            
            self.notify("Power BI login completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            self.notify(f"Login failed: {str(e)}", "ERROR")
            return False
    
    def refresh_dataset(self):
        """Refresh the Power BI dataset"""
        try:
            self.notify("Navigating to dataset page")
            
            # Navigate to dataset page
            self.driver.get(self.dataset_url)
            time.sleep(5)
            
            # Click the Refresh dropdown
            self.notify("Clicking refresh dropdown")
            dropdown_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//span[normalize-space(text())='Refresh']"))
            )
            dropdown_button.click()
            time.sleep(2)
            
            # Click "Refresh now"
            self.notify("Triggering dataset refresh")
            refresh_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@title='Refresh now' and @role='menuitem']//span[normalize-space()='Refresh now']"))
            )
            refresh_button.click()
            
            self.notify("Dataset refresh triggered successfully", "SUCCESS")
            
            # Wait and monitor refresh status
            self.monitor_refresh_status()
            
            return True
            
        except Exception as e:
            logger.error(f"Dataset refresh failed: {str(e)}")
            self.notify(f"Dataset refresh failed: {str(e)}", "ERROR")
            return False
    
    def monitor_refresh_status(self):
        """Monitor the refresh status and notify when complete"""
        try:
            self.notify("Monitoring refresh status...")
            
            # Wait for refresh to start (indicated by progress or status change)
            time.sleep(10)
            
            # Check for refresh completion indicators
            max_wait_time = 300  # 5 minutes maximum wait
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                try:
                    # Look for refresh completion indicators
                    # This might need adjustment based on Power BI's actual UI
                    refresh_status_elements = self.driver.find_elements(
                        By.XPATH, "//div[contains(@class, 'refresh') or contains(text(), 'Last refresh')]"
                    )
                    
                    if refresh_status_elements:
                        # Check if refresh is complete
                        status_text = self.driver.page_source
                        if "completed" in status_text.lower() or "succeeded" in status_text.lower():
                            self.notify("Power BI dataset refresh completed successfully!", "SUCCESS")
                            return True
                        elif "failed" in status_text.lower() or "error" in status_text.lower():
                            self.notify("Power BI dataset refresh failed", "ERROR")
                            return False
                    
                    time.sleep(15)  # Check every 15 seconds
                    
                except Exception as e:
                    logger.debug(f"Status check iteration failed: {str(e)}")
                    time.sleep(15)
            
            # If we reach here, monitoring timed out
            self.notify("Refresh monitoring timed out - refresh may still be in progress", "WARNING")
            return True
            
        except Exception as e:
            logger.error(f"Refresh monitoring failed: {str(e)}")
            self.notify(f"Refresh monitoring failed: {str(e)}", "ERROR")
            return False
    
    def refresh_powerbi_dataset(self):
        """Main method to refresh Power BI dataset"""
        success = False
        
        try:
            if not self.username or not self.password or not self.dataset_url:
                raise ValueError("Missing Power BI credentials or dataset URL")
            
            self.notify("Starting Power BI dataset refresh automation")
            
            # Setup driver
            if not self.setup_driver():
                return False
            
            # Login
            if not self.login_to_powerbi():
                return False
            
            # Refresh dataset
            if not self.refresh_dataset():
                return False
            
            success = True
            self.notify("Power BI refresh automation completed successfully!", "SUCCESS")
            
        except Exception as e:
            logger.error(f"Power BI refresh automation failed: {str(e)}")
            self.notify(f"Power BI refresh automation failed: {str(e)}", "ERROR")
            
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("Chrome driver closed")
        
        return success

# Notification system for Flask integration
class FlaskNotificationHandler:
    def __init__(self, app=None):
        self.app = app
        self.notifications = []
        self.max_notifications = 50
    
    def add_notification(self, notification):
        """Add notification to the queue"""
        self.notifications.append(notification)
        
        # Keep only the most recent notifications
        if len(self.notifications) > self.max_notifications:
            self.notifications = self.notifications[-self.max_notifications:]
        
        # Log the notification
        if self.app:
            with self.app.app_context():
                logger.info(f"Power BI Notification: {notification['message']}")
    
    def get_notifications(self, since_timestamp=None):
        """Get notifications since a specific timestamp"""
        if since_timestamp:
            return [n for n in self.notifications if n['timestamp'] > since_timestamp]
        return self.notifications
    
    def clear_notifications(self):
        """Clear all notifications"""
        self.notifications = []

# Factory function for easy integration
def create_powerbi_refresher(app=None):
    """Create a Power BI refresher with Flask notification integration"""
    refresher = PowerBIRefresher()
    
    if app:
        notification_handler = FlaskNotificationHandler(app)
        refresher.add_notification_callback(notification_handler.add_notification)
        
        # Store handler in app context for access in routes
        app.powerbi_notifications = notification_handler
    
    return refresher

# Async wrapper for background execution
async def refresh_powerbi_async(username=None, password=None, dataset_url=None, notification_callback=None):
    """Async wrapper for Power BI refresh"""
    refresher = PowerBIRefresher(username, password, dataset_url)
    
    if notification_callback:
        refresher.add_notification_callback(notification_callback)
    
    # Run in executor to avoid blocking
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, refresher.refresh_powerbi_dataset)

if __name__ == "__main__":
    # Example usage
    def print_notification(notification):
        print(f"[{notification['timestamp']}] {notification['level']}: {notification['message']}")
    
    refresher = PowerBIRefresher(
        username='aahmad@novelluscapital.co.uk',
        password='BlueWatch804!',
        dataset_url='https://app.powerbi.com/groups/71153f62-9f44-47cd-b6d5-c3e56e8977ba/datasets/b4bb8a57-7172-4545-bda9-add23e41bc11/details?experience=power-bi'
    )
    
    refresher.add_notification_callback(print_notification)
    refresher.refresh_powerbi_dataset()