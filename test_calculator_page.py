import threading
import time
from datetime import date

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
from werkzeug.serving import make_server

from app import app

@pytest.fixture(scope="module")
def live_server():
    port = 5001
    server = make_server("localhost", port, app)
    thread = threading.Thread(target=server.serve_forever)
    thread.setDaemon(True)
    thread.start()
    try:
        yield f"http://localhost:{port}"
    finally:
        server.shutdown()


def _get_chrome_driver():
    chromedriver_autoinstaller.install()
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    try:
        driver = webdriver.Chrome(options=options)
    except Exception:
        pytest.skip("Chrome driver not available")
    return driver


def test_calculator_page_runs_without_js_errors(live_server):
    driver = _get_chrome_driver()
    try:
        driver.get(live_server + "/calculator")
        # Populate required form fields
        driver.find_element(By.ID, "loanName").send_keys("Test Loan")
        driver.find_element(By.ID, "propertyValue").send_keys("500000")
        driver.find_element(By.ID, "grossAmountFixed").send_keys("100000")
        driver.find_element(By.ID, "loanTerm").send_keys("12")
        today = date.today().strftime("%Y-%m-%d")
        driver.find_element(By.ID, "startDate").send_keys(today)
        # Submit form to trigger calculation
        driver.find_element(By.CSS_SELECTOR, "button.calculate-button").click()
        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.ID, "resultsSection").is_displayed()
        )
        logs = [entry for entry in driver.get_log("browser") if entry["level"] == "SEVERE"]
        assert not logs, f"JavaScript errors found: {logs}"
    finally:
        driver.quit()
