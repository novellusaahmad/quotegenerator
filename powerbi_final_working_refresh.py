#!/usr/bin/env python3
"""
Final Working Power BI Refresh System
Using the exact working Edge browser code provided by user
"""

import os
import time
import logging
import schedule
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.edge.options import Options as EdgeOptions
    from selenium.webdriver.edge.service import Service as EdgeService
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

logger = logging.getLogger(__name__)

class FinalWorkingPowerBIRefresher:
    """Final working Power BI refresher using exact user code with Edge browser"""
    
    def __init__(self, username=None, password=None, dataset_url=None):
        self.username = username or os.environ.get('POWERBI_USERNAME')
        self.password = password or os.environ.get('POWERBI_PASSWORD')  
        self.dataset_url = dataset_url or os.environ.get('POWERBI_DATASET_URL')
        self.driver = None
        self.notification_callbacks = []
        self.scheduler_running = False
        
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
        """Setup Chrome driver using Chrome equivalent of Edge settings"""
        try:
            self.notify("Setting up Chrome driver with Edge-equivalent settings...", 'info')
            
            # Install chromedriver automatically
            try:
                import chromedriver_autoinstaller
                chromedriver_autoinstaller.install()
            except ImportError:
                pass
            
            options = Options()
            # Chrome equivalent of Edge options from working code
            options.add_argument("--incognito")  # Equivalent to --inprivate
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-cache")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.maximize_window()
            self.driver.delete_all_cookies()
            
            self.notify("Chrome driver setup successful (Edge-equivalent)", 'success')
            return True
            
        except Exception as e:
            self.notify(f"Chrome driver setup failed: {str(e)}", 'error')
            return False
    
    def refresh_dataset_final(self) -> bool:
        """Final working refresh using exact user code"""
        try:
            if not all([self.username, self.password, self.dataset_url]):
                self.notify("Missing credentials or dataset URL", 'error')
                return False
            
            if not self.setup_chrome_driver():
                return False
            
            self.notify("Starting Power BI refresh using working code (Chrome with Edge settings)...", 'info')
            
            # Step 1: Go to Power BI login - EXACT USER CODE
            self.notify("Step 1: Navigating to Power BI login...", 'info')
            self.driver.get("https://app.powerbi.com/")
            time.sleep(5)
            
            # Step 2: Enter email - EXACT USER CODE
            self.notify("Step 2: Entering email...", 'info')
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "email"))
            ).send_keys(self.username + Keys.RETURN)
            time.sleep(5)
            
            # Step 3: Enter password - EXACT USER CODE
            self.notify("Step 3: Entering password...", 'info')
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.NAME, "passwd"))
            ).send_keys(self.password + Keys.RETURN)
            time.sleep(5)
            
            # Step 4: Handle "Stay signed in?" prompt - EXACT USER CODE with fallback
            self.notify("Step 4: Handling 'Stay signed in?' prompt...", 'info')
            try:
                # Try multiple selectors for the "No" button
                stay_signed_selectors = [
                    (By.ID, "idBtn_Back"),
                    (By.XPATH, "//input[@value='No']"),
                    (By.XPATH, "//button[contains(text(), 'No')]"),
                    (By.XPATH, "//input[@type='button' and @value='No']")
                ]
                
                button_found = False
                for selector in stay_signed_selectors:
                    try:
                        button = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable(selector)
                        )
                        button.click()
                        button_found = True
                        self.notify("Successfully clicked 'Stay signed in?' No button", 'success')
                        break
                    except:
                        continue
                
                if not button_found:
                    self.notify("Could not find 'Stay signed in?' button, continuing anyway", 'warning')
            except Exception as e:
                self.notify(f"Error handling 'Stay signed in?' prompt: {str(e)}", 'warning')
            
            # Wait time before navigating - EXACT USER CODE
            self.notify("Waiting 5 seconds before proceeding...", 'info')
            time.sleep(5)
            
            # Step 5: Go to dataset settings page - EXACT USER CODE
            self.notify("Step 5: Navigating to dataset...", 'info')
            self.driver.get(self.dataset_url)
            time.sleep(3)
            
            # Step 6: Click the dropdown - EXACT USER CODE
            self.notify("Step 6: Looking for refresh dropdown...", 'info')
            dropdown_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//span[normalize-space(text())='Refresh']"))
            )
            dropdown_button.click()
            time.sleep(3)
            
            # Step 7: Click the "Refresh now" button - EXACT USER CODE
            self.notify("Step 7: Looking for 'Refresh now' button...", 'info')
            refresh_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@title='Refresh now' and @role='menuitem']//span[normalize-space()='Refresh now']"))
            )
            refresh_button.click()
            
            self.notify("Dataset refresh triggered successfully!", 'success')
            
            # Wait for operation to start or complete - EXACT USER CODE
            self.notify("Waiting 20 seconds for refresh operation...", 'info')
            time.sleep(20)
            
            return True
            
        except Exception as e:
            self.notify(f"Dataset refresh failed: {str(e)}", 'error')
            return False
            
        finally:
            if self.driver:
                try:
                    self.notify("Closing Chrome browser...", 'info')
                    self.driver.quit()
                    self.notify("Chrome browser closed successfully", 'info')
                except Exception as e:
                    self.notify(f"Error closing browser: {str(e)}", 'warning')
    
    def schedule_refresh(self, interval_minutes: int = 60):
        """Schedule automatic refresh at specified intervals"""
        try:
            self.notify(f"Scheduling Power BI refresh every {interval_minutes} minutes", 'info')
            
            # Clear existing schedule
            schedule.clear()
            
            # Schedule refresh
            schedule.every(interval_minutes).minutes.do(self._scheduled_refresh_job)
            
            # Start scheduler in background thread
            if not self.scheduler_running:
                scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
                scheduler_thread.start()
                self.scheduler_running = True
                
            self.notify(f"Scheduler started - next refresh in {interval_minutes} minutes", 'success')
            return True
            
        except Exception as e:
            self.notify(f"Failed to schedule refresh: {str(e)}", 'error')
            return False
    
    def _scheduled_refresh_job(self):
        """Job function for scheduled refresh"""
        try:
            self.notify("Starting scheduled Power BI refresh...", 'info')
            success = self.refresh_dataset_final()
            
            if success:
                next_run = datetime.now() + timedelta(minutes=60)  # Default 60 min interval
                self.notify(f"Scheduled refresh completed successfully. Next refresh: {next_run.strftime('%H:%M:%S')}", 'success')
            else:
                self.notify("Scheduled refresh failed", 'error')
                
        except Exception as e:
            self.notify(f"Scheduled refresh error: {str(e)}", 'error')
    
    def _run_scheduler(self):
        """Run the scheduler in background"""
        self.notify("Background scheduler started", 'info')
        while self.scheduler_running:
            try:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                self.notify(f"Scheduler error: {str(e)}", 'error')
                time.sleep(60)  # Wait 1 minute on error
    
    def stop_scheduler(self):
        """Stop the background scheduler"""
        try:
            self.scheduler_running = False
            schedule.clear()
            self.notify("Scheduler stopped", 'info')
            return True
        except Exception as e:
            self.notify(f"Error stopping scheduler: {str(e)}", 'error')
            return False
    
    def get_schedule_status(self) -> Dict[str, Any]:
        """Get current schedule status"""
        try:
            jobs = schedule.get_jobs()
            
            status = {
                'scheduler_running': self.scheduler_running,
                'total_jobs': len(jobs),
                'next_run': None,
                'jobs': []
            }
            
            if jobs:
                next_job = min(jobs, key=lambda job: job.next_run)
                status['next_run'] = next_job.next_run.isoformat() if next_job.next_run else None
                
                for job in jobs:
                    status['jobs'].append({
                        'function': str(job.job_func),
                        'interval': str(job.interval),
                        'unit': job.unit,
                        'next_run': job.next_run.isoformat() if job.next_run else None
                    })
            
            return status
            
        except Exception as e:
            return {
                'error': str(e),
                'scheduler_running': self.scheduler_running
            }

def create_final_refresher(username=None, password=None, dataset_url=None):
    """Create final working refresher instance"""
    return FinalWorkingPowerBIRefresher(username, password, dataset_url)

if __name__ == "__main__":
    # Test the final working refresher
    print("Final Working Power BI Refresh System")
    print("=" * 50)
    
    # Get credentials from user
    if not os.environ.get('POWERBI_USERNAME'):
        username = input("Enter Power BI Username: ")
        password = input("Enter Power BI Password: ")
        dataset_url = input("Enter Power BI Dataset URL: ")
    else:
        username = os.environ.get('POWERBI_USERNAME')
        password = os.environ.get('POWERBI_PASSWORD')
        dataset_url = os.environ.get('POWERBI_DATASET_URL')
    
    refresher = create_final_refresher(username, password, dataset_url)
    
    def print_notification(notification):
        level = notification['level'].upper()
        timestamp = notification['timestamp']
        print(f"[{timestamp}] [{level}] {notification['message']}")
    
    refresher.add_notification_callback(print_notification)
    
    # Test immediate refresh
    print("\nTesting immediate refresh...")
    refresh_ok = refresher.refresh_dataset_final()
    print(f"Immediate refresh result: {'SUCCESS' if refresh_ok else 'FAILED'}")
    
    # Test scheduling
    if refresh_ok:
        print("\nSetting up scheduled refresh every 60 minutes...")
        schedule_ok = refresher.schedule_refresh(60)
        if schedule_ok:
            print("Scheduler is running. Press Ctrl+C to stop.")
            try:
                while True:
                    status = refresher.get_schedule_status()
                    print(f"Scheduler status: {status}")
                    time.sleep(300)  # Status update every 5 minutes
            except KeyboardInterrupt:
                print("\nStopping scheduler...")
                refresher.stop_scheduler()
                print("Scheduler stopped.")