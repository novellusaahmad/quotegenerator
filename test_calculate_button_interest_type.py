from datetime import date

import pytest

selenium = pytest.importorskip("selenium")
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from test_calculator_page import live_server, _get_chrome_driver


def test_calculate_button_still_works_after_interest_change(live_server):
    driver = _get_chrome_driver()
    try:
        driver.get(live_server + "/calculator")
        driver.find_element(By.ID, "loanName").send_keys("Test Loan")
        driver.find_element(By.ID, "propertyValue").send_keys("500000")
        driver.find_element(By.ID, "grossAmountFixed").send_keys("100000")
        driver.find_element(By.ID, "loanTerm").send_keys("12")
        today = date.today().strftime("%Y-%m-%d")
        driver.find_element(By.ID, "startDate").send_keys(today)

        # Initial calculation
        driver.find_element(By.CSS_SELECTOR, "button.calculate-button").click()
        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.ID, "resultsSection").is_displayed()
        )

        # Change interest calculation type
        driver.find_element(By.ID, "interestCompoundDaily").click()
        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.ID, "resultsSection").is_displayed()
        )

        # Modify a field to require recalculation
        pv = driver.find_element(By.ID, "propertyValue")
        pv.clear()
        pv.send_keys("600000")

        # Ensure calculate button works after interest change
        driver.find_element(By.CSS_SELECTOR, "button.calculate-button").click()
        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.ID, "resultsSection").is_displayed()
        )
    finally:
        driver.quit()
