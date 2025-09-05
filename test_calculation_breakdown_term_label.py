import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from test_calculator_page import live_server, _get_chrome_driver


def _open_breakdown(driver):
    driver.find_element(By.ID, "viewBreakdownBtn").click()
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "calculationBreakdownModal"))
    )
    content = WebDriverWait(driver, 10).until(
        lambda d: d.find_element(By.ID, "calculationBreakdownContent").text
    )
    return content


def test_breakdown_displays_loan_term_days_when_end_date_used(live_server):
    driver = _get_chrome_driver()
    try:
        driver.get(live_server + "/calculator")
        driver.find_element(By.ID, "loanName").send_keys("Test Loan")
        driver.find_element(By.ID, "propertyValue").send_keys("500000")
        driver.find_element(By.ID, "grossAmountFixed").send_keys("100000")
        driver.find_element(By.ID, "startDate").send_keys("2024-01-01")
        driver.find_element(By.ID, "loanEndDateOption").click()
        driver.find_element(By.ID, "endDate").send_keys("2024-03-01")
        driver.find_element(By.CSS_SELECTOR, "button.calculate-button").click()
        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.ID, "resultsSection").is_displayed()
        )
        content = _open_breakdown(driver)
        assert "Loan Term (days)" in content
    finally:
        driver.quit()


def test_breakdown_displays_loan_term_months_without_end_date(live_server):
    driver = _get_chrome_driver()
    try:
        driver.get(live_server + "/calculator")
        driver.find_element(By.ID, "loanName").send_keys("Test Loan")
        driver.find_element(By.ID, "propertyValue").send_keys("500000")
        driver.find_element(By.ID, "grossAmountFixed").send_keys("100000")
        driver.find_element(By.ID, "loanTerm").send_keys("12")
        driver.find_element(By.ID, "startDate").send_keys("2024-01-01")
        driver.find_element(By.CSS_SELECTOR, "button.calculate-button").click()
        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.ID, "resultsSection").is_displayed()
        )
        content = _open_breakdown(driver)
        assert "Loan Term (months)" in content
    finally:
        driver.quit()
