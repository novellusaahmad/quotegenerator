from urllib.parse import urlencode

import pytest

try:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
except Exception:  # pragma: no cover - skip if selenium not installed
    pytest.skip("Selenium not available", allow_module_level=True)

from test_calculator_page import live_server, _get_chrome_driver


def test_editing_populates_all_fields(live_server):
    driver = _get_chrome_driver()
    try:
        params = {
            "edit": "true",
            "loanId": "1",
            "loanName": "Edit Loan",
            "loan_type": "bridge",
            "gross_amount": "250000",
            "net_amount": "200000",
            "gross_amount_percentage": "50",
            "property_value": "500000",
            "annual_rate": "12",
            "monthly_rate": "1",
            "loan_term": "12",
            "start_date": "2024-01-01",
            "repayment_option": "service_and_capital",
            "arrangement_fee_percentage": "3",
            "legal_fees": "1000",
            "site_visit_fee": "200",
            "title_insurance_rate": "0.02",
            "payment_timing": "arrears",
            "payment_frequency": "quarterly",
            "capital_repayment": "500",
            "amount_input_type": "gross",
            "gross_amount_type": "percentage",
            "rate_input_type": "annual",
            "interest_type": "compound_monthly",
            "use_360_days": "true",
            "currency": "EUR",
        }
        url = f"{live_server}/calculator?{urlencode(params)}"
        driver.get(url)

        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.ID, "loanName").get_attribute("value") == "Edit Loan"
        )

        assert driver.find_element(By.ID, "arrangementFeePercentage").get_attribute("value") == "3"
        assert driver.find_element(By.ID, "legalFees").get_attribute("value") == "1000"
        assert driver.find_element(By.ID, "siteVisitFee").get_attribute("value") == "200"
        assert driver.find_element(By.ID, "titleInsuranceRate").get_attribute("value") == "0.02"
        assert driver.find_element(By.ID, "annualRateValue").get_attribute("value") == "12"
        assert driver.find_element(By.ID, "interestCompoundMonthly").is_selected()
        assert driver.find_element(By.ID, "use360Days").is_selected()
        assert driver.find_element(By.ID, "grossAmount").is_selected()
        assert driver.find_element(By.ID, "grossPercentage").is_selected()
        assert driver.find_element(By.ID, "paymentInArrears").is_selected()
        assert driver.find_element(By.ID, "paymentQuarterly").is_selected()
        assert driver.find_element(By.ID, "capitalRepayment").get_attribute("value") == "500"
        assert driver.find_element(By.ID, "loanTypeBridge").is_selected()
        assert driver.find_element(By.ID, "currencyEUR").is_selected()
        assert driver.find_element(By.ID, "repaymentServiceCapital").is_selected()
    finally:
        driver.quit()


def test_editing_populates_tranches(live_server):
    driver = _get_chrome_driver()
    try:
        params = {
            "edit": "true",
            "loanId": "2",
            "loanName": "Dev Loan",
            "loan_type": "development2",
            "tranche_mode": "manual",
            "tranche_amounts[0]": "10000",
            "tranche_dates[0]": "2024-01-01",
            "tranche_rates[0]": "10",
            "tranche_descriptions[0]": "Phase 1",
            "tranche_amounts[1]": "20000",
            "tranche_dates[1]": "2024-06-01",
            "tranche_rates[1]": "11",
            "tranche_descriptions[1]": "Phase 2",
        }
        url = f"{live_server}/calculator?{urlencode(params)}"
        driver.get(url)

        WebDriverWait(driver, 10).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, "#trancheContainer .tranche-item")) == 2
        )
        items = driver.find_elements(By.CSS_SELECTOR, "#trancheContainer .tranche-item")
        first = items[0]
        second = items[1]
        assert first.find_element(By.CSS_SELECTOR, 'input[id*="trancheAmount"]').get_attribute("value") == "10000"
        assert first.find_element(By.CSS_SELECTOR, 'input[id*="trancheDate"]').get_attribute("value") == "2024-01-01"
        assert first.find_element(By.CSS_SELECTOR, 'input[id*="trancheRate"]').get_attribute("value") == "10"
        assert first.find_element(By.CSS_SELECTOR, 'input[id*="trancheDescription"]').get_attribute("value") == "Phase 1"
        assert second.find_element(By.CSS_SELECTOR, 'input[id*="trancheAmount"]').get_attribute("value") == "20000"
        assert second.find_element(By.CSS_SELECTOR, 'input[id*="trancheDate"]').get_attribute("value") == "2024-06-01"
        assert second.find_element(By.CSS_SELECTOR, 'input[id*="trancheRate"]').get_attribute("value") == "11"
        assert second.find_element(By.CSS_SELECTOR, 'input[id*="trancheDescription"]').get_attribute("value") == "Phase 2"
    finally:
        driver.quit()


def test_editing_shows_capital_repayment_section(live_server):
    driver = _get_chrome_driver()
    try:
        params = {
            "edit": "true",
            "loanId": "3",
            "loanName": "Cap Loan",
            "loan_type": "bridge",
            "repayment_option": "service_and_capital",
            "capital_repayment": "750",
            "payment_timing": "arrears",
            "payment_frequency": "monthly",
        }
        url = f"{live_server}/calculator?{urlencode(params)}"
        driver.get(url)

        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.ID, "capitalRepaymentSection").is_displayed()
        )
        assert driver.find_element(By.ID, "capitalRepaymentSection").is_displayed()
        assert not driver.find_element(By.ID, "flexiblePaymentSection").is_displayed()
    finally:
        driver.quit()


def test_editing_shows_flexible_payment_section(live_server):
    driver = _get_chrome_driver()
    try:
        params = {
            "edit": "true",
            "loanId": "4",
            "loanName": "Flex Loan",
            "loan_type": "bridge",
            "repayment_option": "flexible_payment",
            "flexible_payment": "1000",
            "payment_timing": "arrears",
            "payment_frequency": "monthly",
        }
        url = f"{live_server}/calculator?{urlencode(params)}"
        driver.get(url)

        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.ID, "flexiblePaymentSection").is_displayed()
        )
        assert driver.find_element(By.ID, "flexiblePaymentSection").is_displayed()
        assert not driver.find_element(By.ID, "capitalRepaymentSection").is_displayed()
    finally:
        driver.quit()
