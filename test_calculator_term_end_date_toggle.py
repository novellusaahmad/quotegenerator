import pytest
from selenium.webdriver.common.by import By

from test_calculator_page import live_server, _get_chrome_driver


def test_toggle_preserves_values(live_server):
    driver = _get_chrome_driver()
    try:
        driver.get(live_server + "/calculator")
        start = driver.find_element(By.ID, "startDate")
        start.clear()
        start.send_keys("2024-01-15")
        term = driver.find_element(By.ID, "loanTerm")
        term.clear()
        term.send_keys("12")
        driver.execute_script("calculateEndDate();")
        initial_term = term.get_attribute("value")
        initial_end = driver.find_element(By.ID, "endDate").get_attribute("value")
        for _ in range(3):
            driver.find_element(By.ID, "loanEndDateOption").click()
            end_val = driver.find_element(By.ID, "endDate").get_attribute("value")
            assert end_val == initial_end
            driver.find_element(By.ID, "loanTermOption").click()
            term_val = term.get_attribute("value")
            assert term_val == initial_term
    finally:
        driver.quit()
