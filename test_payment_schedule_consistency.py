#!/usr/bin/env python3
"""
Test script to validate payment schedule consistency between tranche release and interest calculation base.
This addresses the critical issue where tranche release (£126,488.08) != interest calculation base (£126,329).
"""

import sys
import os
import types
import pytest
try:
    import requests
except ModuleNotFoundError:  # Provide minimal stub if requests is missing
    requests = types.SimpleNamespace()
import json
from decimal import Decimal

# Provide a minimal stub for dateutil.relativedelta to avoid external dependency
relativedelta_module = types.ModuleType('relativedelta')

class relativedelta:
    def __init__(self, months=0):
        self.months = months

    def __radd__(self, other):
        from datetime import date
        # Add months to a date or datetime object
        month = other.month - 1 + self.months
        year = other.year + month // 12
        month = month % 12 + 1
        day = min(other.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                              31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
        return other.replace(year=year, month=month, day=day)

relativedelta_module.relativedelta = relativedelta
dateutil_module = types.ModuleType('dateutil')
dateutil_module.relativedelta = relativedelta_module
sys.modules['dateutil'] = dateutil_module
sys.modules['dateutil.relativedelta'] = relativedelta_module

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from calculations import LoanCalculator

def test_payment_schedule_consistency():
    """Test that tranche release and interest calculation base match exactly"""
    
    print("=" * 80)
    print("PAYMENT SCHEDULE CONSISTENCY TEST")
    print("=" * 80)
    
    calculator = LoanCalculator()
    
    # Test parameters that previously showed inconsistency
    test_params = {
        'loan_type': 'development',
        'net_amount': 800000,
        'annual_rate': 12,
        'loan_term': 18,
        'property_value': 10000000,
        'arrangement_fee_rate': 2,  # Use rate instead of percentage
        'legal_fees': 7587.94,
        'site_visit_fee': 0,
        'title_insurance_rate': 0,
        'currency': 'GBP',
        'repayment_option': 'none',
        'interest_type': 'compound_daily',
        'start_date': '2025-07-23',
        'day1_advance': 100000,
        'tranches': [
            {'amount': 70000, 'date': '2025-07-23', 'rate': 12, 'description': 'Tranche 1'}
        ] * 10  # 10 tranches of £70,000 each
    }
    
    print(f"Testing with parameters:")
    print(f"- Net Amount: £{test_params['net_amount']:,}")
    print(f"- Day 1 Advance: £{test_params['day1_advance']:,}")
    print(f"- Annual Rate: {test_params['annual_rate']}%")
    print(f"- Arrangement Fee Rate: {test_params['arrangement_fee_rate']}%")
    print(f"- Legal Fees: £{test_params['legal_fees']:,}")
    print(f"- Tranches: {len(test_params['tranches'])} × £{test_params['tranches'][0]['amount']:,}")
    print()
    
    try:
        # Run the calculation
        result = calculator.calculate_development_loan(test_params)
        
        # Check if calculation succeeded
        if 'detailed_payment_schedule' not in result or not result['detailed_payment_schedule']:
            print("❌ FAILED: No detailed payment schedule generated")
            return False
            
        # Get the first month's data (where the issue occurs)
        first_month = result['detailed_payment_schedule'][0]
        
        print("FIRST MONTH PAYMENT SCHEDULE ANALYSIS:")
        print("-" * 50)
        
        # Extract tranche release amount
        tranche_release_str = first_month.get('tranche_release', '—')
        if tranche_release_str == '—':
            print("❌ FAILED: No tranche release in first month")
            return False
            
        # Parse tranche release amount (remove currency symbol and commas)
        tranche_release = Decimal(tranche_release_str.replace('£', '').replace(',', ''))
        print(f"Tranche Release: {tranche_release_str}")
        
        # Extract interest calculation base
        interest_calc_str = first_month.get('interest_calculation', '')
        if not interest_calc_str or interest_calc_str == '—':
            print("❌ FAILED: No interest calculation in first month")
            return False
            
        print(f"Interest Calculation: {interest_calc_str}")
        
        # Parse interest calculation base (extract the amount before the multiplication sign)
        try:
            # Format: "£126,329 × (1 + 0.000329)^31"
            calc_base_str = interest_calc_str.split(' ×')[0].replace('£', '').replace(',', '')
            calc_base = Decimal(calc_base_str)
            print(f"Interest Calculation Base: £{calc_base:,}")
        except:
            print(f"❌ FAILED: Could not parse interest calculation base from: {interest_calc_str}")
            return False
        
        # Calculate expected Day 1 tranche release
        arrangement_fee = Decimal(str(result.get('arrangementFee', 0)))
        legal_fees = Decimal(str(test_params['legal_fees']))
        site_visit_fee = Decimal(str(test_params['site_visit_fee']))
        title_insurance = Decimal(str(result.get('titleInsurance', 0)))
        day1_advance = Decimal(str(test_params['day1_advance']))
        
        expected_tranche_release = day1_advance + arrangement_fee + legal_fees + site_visit_fee + title_insurance
        
        print()
        print("EXPECTED CALCULATION:")
        print(f"Day 1 Advance:     £{day1_advance:,}")
        print(f"Arrangement Fee:   £{arrangement_fee:,.2f}")
        print(f"Legal Fees:        £{legal_fees:,.2f}")
        print(f"Site Visit Fee:    £{site_visit_fee:,.2f}")
        print(f"Title Insurance:   £{title_insurance:,.2f}")
        print(f"Expected Total:    £{expected_tranche_release:,.2f}")
        print()
        
        # Test consistency
        print("CONSISTENCY CHECK:")
        print("-" * 30)
        
        # Check 1: Tranche release matches expected calculation
        tranche_diff = abs(tranche_release - expected_tranche_release)
        if tranche_diff < Decimal('0.01'):
            print(f"✅ Tranche Release Calculation: CORRECT (diff: £{tranche_diff:.2f})")
        else:
            print(f"❌ Tranche Release Calculation: INCORRECT")
            print(f"   Expected: £{expected_tranche_release:,.2f}")
            print(f"   Actual:   £{tranche_release:,.2f}")
            print(f"   Difference: £{tranche_diff:.2f}")
        
        # Check 2: Interest calculation base matches tranche release
        consistency_diff = abs(calc_base - tranche_release)
        if consistency_diff < Decimal('0.01'):
            print(f"✅ Interest Calculation Base: CONSISTENT (diff: £{consistency_diff:.2f})")
            consistency_passed = True
        else:
            print(f"❌ Interest Calculation Base: INCONSISTENT")
            print(f"   Tranche Release:       £{tranche_release:,.2f}")
            print(f"   Interest Calc Base:    £{calc_base:,.2f}")
            print(f"   Difference:            £{consistency_diff:.2f}")
            consistency_passed = False
        
        print()
        
        if consistency_passed and tranche_diff < Decimal('0.01'):
            print("🎉 ALL TESTS PASSED: Payment schedule is consistent!")
            return True
        else:
            print("❌ TESTS FAILED: Payment schedule has consistency issues!")
            return False
            
    except Exception as e:
        print(f"❌ CALCULATION ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoint():
    """Test the API endpoint directly"""

    pytest.importorskip("requests")
    if not hasattr(requests, "post"):
        pytest.skip("requests library not available")

    print("\n" + "=" * 80)
    print("API ENDPOINT TEST")
    print("=" * 80)
    
    test_data = {
        "loan_type": "development",
        "net_amount": 800000,
        "annual_rate": 12,
        "loan_term": 18,
        "property_value": 10000000,
        "arrangement_fee_percentage": 2,
        "legal_costs": 7587.94,
        "site_visit_fee": 0,
        "title_insurance_rate": 0,
        "currency": "GBP",
        "repayment_option": "none",
        "interest_calculation_type": "compound_daily",
        "start_date": "2025-07-23",
        "day1_advance": 100000,
        "tranches": [
            {"amount": 70000, "date": "2025-07-23", "rate": 12, "description": "Tranche 1"}
        ]
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/api/calculate',
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=30
        )
        
        print(f"API Response Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ API ERROR: {response.text}")
            return False
            
        result = response.json()
        
        if 'error' in result:
            print(f"❌ CALCULATION ERROR: {result['error']}")
            return False
            
        if 'detailed_payment_schedule' not in result:
            print("❌ NO PAYMENT SCHEDULE: Missing detailed_payment_schedule in response")
            return False
            
        schedule = result['detailed_payment_schedule']
        if not schedule:
            print("❌ EMPTY SCHEDULE: detailed_payment_schedule is empty")
            return False
            
        first_month = schedule[0]
        print(f"✅ API SUCCESS: Got {len(schedule)} payment periods")
        print(f"First month tranche release: {first_month.get('tranche_release', 'N/A')}")
        print(f"First month interest calc: {first_month.get('interest_calculation', 'N/A')}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API CONNECTION ERROR: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {str(e)}")
        return False

def run_multiple_scenarios():
    """Test multiple scenarios to ensure robustness"""
    
    print("\n" + "=" * 80)
    print("MULTIPLE SCENARIO TESTING")
    print("=" * 80)
    
    scenarios = [
        {
            'name': 'Standard Case',
            'params': {
                'net_amount': 800000,
                'day1_advance': 100000,
                'annual_rate': 12,
                'arrangement_fee_rate': 2,
                'legal_fees': 7587.94
            }
        },
        {
            'name': 'Different Rate',
            'params': {
                'net_amount': 800000,
                'day1_advance': 100000,
                'annual_rate': 15,
                'arrangement_fee_rate': 2,
                'legal_fees': 7587.94
            }
        },
        {
            'name': 'Different Day 1 Advance',
            'params': {
                'net_amount': 800000,
                'day1_advance': 150000,
                'annual_rate': 12,
                'arrangement_fee_rate': 2,
                'legal_fees': 7587.94
            }
        },
        {
            'name': 'Higher Legal Fees',
            'params': {
                'net_amount': 800000,
                'day1_advance': 100000,
                'annual_rate': 12,
                'arrangement_fee_rate': 2,
                'legal_fees': 15000
            }
        }
    ]
    
    calculator = LoanCalculator()
    all_passed = True
    
    for scenario in scenarios:
        print(f"\nTesting: {scenario['name']}")
        print("-" * 40)
        
        # Build full params
        full_params = {
            'loan_type': 'development',
            'property_value': 10000000,
            'loan_term': 18,
            'site_visit_fee': 0,
            'title_insurance_rate': 0,
            'currency': 'GBP',
            'repayment_option': 'none',
            'interest_type': 'compound_daily',
            'start_date': '2025-07-23',
            'tranches': [
                {'amount': 70000, 'date': '2025-07-23', 'rate': 12, 'description': 'Tranche 1'}
            ]
        }
        full_params.update(scenario['params'])
        
        try:
            result = calculator.calculate_development_loan(full_params)
            
            if 'detailed_payment_schedule' not in result or not result['detailed_payment_schedule']:
                print(f"❌ {scenario['name']}: No payment schedule")
                all_passed = False
                continue
                
            first_month = result['detailed_payment_schedule'][0]
            tranche_release_str = first_month.get('tranche_release', '—')
            interest_calc_str = first_month.get('interest_calculation', '')
            
            if tranche_release_str == '—' or not interest_calc_str:
                print(f"❌ {scenario['name']}: Missing data")
                all_passed = False
                continue
                
            # Quick consistency check
            tranche_amount = Decimal(tranche_release_str.replace('£', '').replace(',', ''))
            calc_base_str = interest_calc_str.split(' ×')[0].replace('£', '').replace(',', '')
            calc_base = Decimal(calc_base_str)
            
            diff = abs(tranche_amount - calc_base)
            if diff < Decimal('0.01'):
                print(f"✅ {scenario['name']}: CONSISTENT (diff: £{diff:.2f})")
            else:
                print(f"❌ {scenario['name']}: INCONSISTENT (diff: £{diff:.2f})")
                print(f"   Tranche: £{tranche_amount:,} vs Calc Base: £{calc_base:,}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ {scenario['name']}: ERROR - {str(e)}")
            all_passed = False
    
    return all_passed

if __name__ == '__main__':
    print("Starting comprehensive payment schedule consistency tests...")
    
    # Test 1: Direct calculation
    test1_passed = test_payment_schedule_consistency()
    
    # Test 2: API endpoint
    test2_passed = test_api_endpoint()
    
    # Test 3: Multiple scenarios
    test3_passed = run_multiple_scenarios()
    
    print("\n" + "=" * 80)
    print("FINAL TEST RESULTS")
    print("=" * 80)
    print(f"Direct Calculation Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"API Endpoint Test:       {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"Multiple Scenarios Test: {'✅ PASSED' if test3_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed and test3_passed:
        print("\n🎉 ALL TESTS PASSED! Payment schedule consistency is fixed!")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED! Issues still need to be resolved.")
        sys.exit(1)