import pytest
from selenium.webdriver.common.by import By

from test_calculator_page import live_server, _get_chrome_driver


def test_end_date_populates_term(live_server):
    driver = _get_chrome_driver()
    try:
        driver.get(live_server + "/calculator")
        start = driver.find_element(By.ID, "startDate")
        start.clear()
        start.send_keys("2024-01-01")
        driver.find_element(By.ID, "loanEndDateOption").click()
        end = driver.find_element(By.ID, "endDate")
        end.clear()
        end.send_keys("2024-12-31")
        driver.execute_script("calculateEndDate();")
        term_val = driver.find_element(By.ID, "loanTerm").get_attribute("value")
        assert term_val == "12"
    finally:
        driver.quit()
