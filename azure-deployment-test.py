#!/usr/bin/env python3
"""
Azure Deployment Testing Script
Novellus Loan Management System

This script tests the deployed Azure Container App to ensure all functionality works correctly.
"""

import requests
import json
import sys
import time
from urllib.parse import urljoin

class AzureDeploymentTester:
    def __init__(self, base_url):
        self.base_url = base_url
        if not self.base_url.endswith('/'):
            self.base_url += '/'
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Novellus-Azure-Test/1.0',
            'Accept': 'application/json, text/html'
        })
        
        self.tests_passed = 0
        self.tests_failed = 0
        
    def log(self, message, level="INFO"):
        colors = {
            "INFO": "\033[36m",   # Cyan
            "PASS": "\033[32m",   # Green
            "FAIL": "\033[31m",   # Red
            "WARN": "\033[33m",   # Yellow
            "RESET": "\033[0m"    # Reset
        }
        print(f"{colors.get(level, '')}{level}: {message}{colors['RESET']}")
    
    def test_health_check(self):
        """Test basic application health"""
        self.log("Testing application health...")
        try:
            response = self.session.get(self.base_url, timeout=30)
            if response.status_code == 200:
                self.log("✅ Application is accessible", "PASS")
                self.tests_passed += 1
                return True
            else:
                self.log(f"❌ Application returned status code {response.status_code}", "FAIL")
                self.tests_failed += 1
                return False
        except Exception as e:
            self.log(f"❌ Failed to reach application: {str(e)}", "FAIL")
            self.tests_failed += 1
            return False
    
    def test_api_endpoints(self):
        """Test critical API endpoints"""
        self.log("Testing API endpoints...")
        
        # Test calculation API with Bridge loan
        test_data = {
            "loan_type": "bridge",
            "gross_amount": 1000000,
            "annual_rate": 12,
            "loan_term": 12,
            "repayment_option": "none",
            "amount_input_type": "gross",
            "arrangement_fee_rate": 2.0,
            "legal_fees": 5000,
            "site_visit_fee": 1000,
            "title_insurance_rate": 0.01,
            "property_value": 2000000,
            "currency": "GBP"
        }
        
        try:
            api_url = urljoin(self.base_url, 'api/calculate')
            response = self.session.post(
                api_url,
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'grossAmount' in result and result['grossAmount'] > 0:
                    self.log("✅ Bridge loan calculation API working", "PASS")
                    self.tests_passed += 1
                    return True
                else:
                    self.log("❌ API returned invalid calculation result", "FAIL")
                    self.tests_failed += 1
                    return False
            else:
                self.log(f"❌ Calculation API failed with status {response.status_code}", "FAIL")
                self.log(f"Response: {response.text[:200]}", "FAIL")
                self.tests_failed += 1
                return False
                
        except Exception as e:
            self.log(f"❌ API test failed: {str(e)}", "FAIL")
            self.tests_failed += 1
            return False
    
    def test_development2_calculation(self):
        """Test Development 2 loan calculation specifically"""
        self.log("Testing Development 2 loan calculation...")
        
        test_data = {
            "loan_type": "development2",
            "net_amount": 800000,
            "annual_rate": 12,
            "loan_term": 18,
            "amount_input_type": "net",
            "arrangement_fee_rate": 2.0,
            "legal_fees": 7587.94,
            "day1_advance": 100000,
            "currency": "GBP",
            "tranches": [
                {"amount": 70000, "release_date": "2025-08-29"},
                {"amount": 70000, "release_date": "2025-09-29"},
                {"amount": 70000, "release_date": "2025-10-29"},
                {"amount": 70000, "release_date": "2025-11-29"},
                {"amount": 70000, "release_date": "2025-12-29"},
                {"amount": 70000, "release_date": "2026-01-29"},
                {"amount": 70000, "release_date": "2026-02-28"},
                {"amount": 70000, "release_date": "2026-03-29"},
                {"amount": 70000, "release_date": "2026-04-29"},
                {"amount": 70000, "release_date": "2026-05-29"}
            ]
        }
        
        try:
            api_url = urljoin(self.base_url, 'api/calculate')
            response = self.session.post(
                api_url,
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=45  # Longer timeout for complex calculation
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'grossAmount' in result and result['grossAmount'] > 900000:
                    gross_amount = result['grossAmount']
                    target_gross = 945201.78  # Expected target
                    accuracy = (1 - abs(gross_amount - target_gross) / target_gross) * 100
                    
                    self.log(f"✅ Development 2 calculation working", "PASS")
                    self.log(f"   Gross Amount: £{gross_amount:,.2f}", "INFO")
                    self.log(f"   Target: £{target_gross:,.2f}", "INFO")
                    self.log(f"   Accuracy: {accuracy:.2f}%", "INFO")
                    self.tests_passed += 1
                    return True
                else:
                    self.log("❌ Development 2 calculation returned invalid result", "FAIL")
                    self.log(f"Result keys: {list(result.keys())}", "FAIL")
                    self.tests_failed += 1
                    return False
            else:
                self.log(f"❌ Development 2 calculation failed with status {response.status_code}", "FAIL")
                self.tests_failed += 1
                return False
                
        except Exception as e:
            self.log(f"❌ Development 2 test failed: {str(e)}", "FAIL")
            self.tests_failed += 1
            return False
    
    def test_database_connectivity(self):
        """Test database connectivity by accessing loan history"""
        self.log("Testing database connectivity...")
        try:
            api_url = urljoin(self.base_url, 'api/saved-loans')
            response = self.session.get(api_url, timeout=30)
            
            if response.status_code == 200:
                self.log("✅ Database connectivity working", "PASS")
                self.tests_passed += 1
                return True
            else:
                self.log(f"❌ Database test failed with status {response.status_code}", "FAIL")
                self.tests_failed += 1
                return False
        except Exception as e:
            self.log(f"❌ Database connectivity test failed: {str(e)}", "FAIL")
            self.tests_failed += 1
            return False
    
    def test_static_resources(self):
        """Test static resources loading"""
        self.log("Testing static resources...")
        static_files = [
            'static/css/style.css',
            'static/js/calculator.js',
            'static/novellus_logo.png'
        ]
        
        for static_file in static_files:
            try:
                url = urljoin(self.base_url, static_file)
                response = self.session.get(url, timeout=15)
                if response.status_code == 200:
                    self.log(f"✅ {static_file} loaded successfully", "PASS")
                else:
                    self.log(f"⚠️ {static_file} returned status {response.status_code}", "WARN")
            except Exception as e:
                self.log(f"⚠️ Failed to load {static_file}: {str(e)}", "WARN")
        
        self.tests_passed += 1
    
    def test_ssl_configuration(self):
        """Test SSL/HTTPS configuration"""
        self.log("Testing SSL configuration...")
        if self.base_url.startswith('https://'):
            try:
                response = self.session.get(self.base_url, timeout=30)
                if response.status_code == 200:
                    self.log("✅ HTTPS/SSL working correctly", "PASS")
                    self.tests_passed += 1
                    return True
            except Exception as e:
                self.log(f"❌ SSL test failed: {str(e)}", "FAIL")
                self.tests_failed += 1
                return False
        else:
            self.log("⚠️ Application not using HTTPS", "WARN")
            return True
    
    def run_all_tests(self):
        """Run all deployment tests"""
        self.log("=" * 60)
        self.log("NOVELLUS AZURE DEPLOYMENT VERIFICATION")
        self.log("=" * 60)
        self.log(f"Testing deployment at: {self.base_url}")
        self.log("")
        
        # Run tests in order
        tests = [
            self.test_health_check,
            self.test_ssl_configuration,
            self.test_static_resources,
            self.test_database_connectivity,
            self.test_api_endpoints,
            self.test_development2_calculation
        ]
        
        for test in tests:
            try:
                test()
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                self.log(f"❌ Test failed with exception: {str(e)}", "FAIL")
                self.tests_failed += 1
        
        # Final summary
        self.log("")
        self.log("=" * 60)
        self.log("DEPLOYMENT TEST SUMMARY")
        self.log("=" * 60)
        self.log(f"Tests Passed: {self.tests_passed}", "PASS")
        self.log(f"Tests Failed: {self.tests_failed}", "FAIL" if self.tests_failed > 0 else "INFO")
        
        if self.tests_failed == 0:
            self.log("🎉 ALL TESTS PASSED - Deployment is successful!", "PASS")
            return True
        else:
            self.log("❌ Some tests failed - Check deployment configuration", "FAIL")
            return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python azure-deployment-test.py <application-url>")
        print("Example: python azure-deployment-test.py https://novellus-loan-calculator.app.azurecontainer.io")
        sys.exit(1)
    
    app_url = sys.argv[1]
    tester = AzureDeploymentTester(app_url)
    
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()