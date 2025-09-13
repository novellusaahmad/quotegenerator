#!/usr/bin/env python3
"""
One-Click Scenario Comparison Tool
Novellus Loan Management System

Compare multiple loan scenarios side-by-side with different parameters
"""

import json
import logging
from datetime import datetime, timedelta
from calculations import LoanCalculator
from decimal import Decimal

logger = logging.getLogger(__name__)

class ScenarioComparison:
    """Compare multiple loan scenarios and summarize key metrics."""

    # Map canonical metric names to possible result keys produced by the
    # calculation engine. The calculation output mixes camelCase and
    # snake_case, and some fields have multiple historical variants.
    # These aliases ensure the comparison table can find the relevant
    # value regardless of which variant is present.
    METRIC_ALIASES = {
        'propertyValue': ['propertyValue', 'property_value'],
        'grossAmount': ['grossAmount', 'gross_amount'],
        'startDate': ['start_date', 'startDate'],
        'endDate': ['end_date', 'endDate'],
        'loanTerm': ['loanTerm', 'loan_term'],
        'loanTermDays': ['loanTermDays', 'loan_term_days'],
        'netAdvance': ['netAdvance', 'net_advance'],
        'totalNetAdvance': [
            'totalNetAdvance',
            'total_net_advance',
            'netAdvance',
            'net_advance',
        ],
        'totalInterest': ['totalInterest', 'total_interest'],
        'arrangementFee': ['arrangementFee', 'arrangement_fee'],
        'legalCosts': ['legalCosts', 'legalFees', 'totalLegalFees', 'legal_costs'],
        'siteVisitFee': ['siteVisitFee', 'site_visit_fee'],
        'titleInsurance': ['titleInsurance', 'title_insurance'],
        'ltv': ['ltv', 'ltv_ratio'],
        'endLTV': ['endLTV', 'end_ltv', 'endLtv'],
        'interestSavings': ['interestSavings', 'interest_savings'],
        'savingsPercentage': ['savingsPercentage', 'savings_percent'],
    }
    def __init__(self):
        # Use the same loan calculation engine as the main calculator page
        self.calculation_engine = LoanCalculator()
        self.scenarios = []
        
    def add_scenario(self, name, parameters):
        """Add a scenario to compare"""
        scenario = {
            'name': name,
            'parameters': parameters,
            'results': None,
            'timestamp': datetime.now().isoformat()
        }
        self.scenarios.append(scenario)
        return len(self.scenarios) - 1  # Return scenario index
    
    def calculate_scenario(self, scenario_index):
        """Calculate results for a specific scenario"""
        if scenario_index >= len(self.scenarios):
            raise ValueError("Invalid scenario index")
        
        scenario = self.scenarios[scenario_index]
        parameters = scenario['parameters']
        
        try:
            # Use the main calculate_loan method with parameters dict
            results = self.calculation_engine.calculate_loan(parameters)
            
            scenario['results'] = results
            scenario['calculated_at'] = datetime.now().isoformat()
            
            return results
            
        except Exception as e:
            logger.error(f"Scenario calculation failed: {str(e)}")
            scenario['error'] = str(e)
            raise
    
    def calculate_all_scenarios(self):
        """Calculate results for all scenarios"""
        results = []
        for i in range(len(self.scenarios)):
            try:
                result = self.calculate_scenario(i)
                results.append(result)
            except Exception as e:
                results.append({'error': str(e)})
        return results

    def _get_result_value(self, results, metric, params=None):
        """Retrieve a metric value from calculation results handling key variants.

        If a metric isn't present (or is zero) in the calculation results,
        attempt to derive it from the original scenario parameters. This is
        especially useful for fee values which may not be included in some
        calculation outputs but can be computed directly from the inputs.
        """

        keys = self.METRIC_ALIASES.get(metric, [metric])
        value = None
        for key in keys:
            if key in results and results[key] not in (None, 'N/A'):
                value = results[key]
                break

        if value not in (None, 0):
            return value

        # For non-fee metrics return the value (even if 0)
        fee_metrics = {'arrangementFee', 'siteVisitFee', 'titleInsurance', 'legalCosts'}
        if metric not in fee_metrics:
            return value

        if not params:
            return value

        try:
            if metric == 'arrangementFee':
                gross = params.get('gross_amount') or params.get('grossAmount')
                rate = params.get('arrangement_fee_rate') or params.get('arrangementFeeRate')
                if gross and rate:
                    return float(gross) * float(rate) / 100.0
            elif metric == 'siteVisitFee':
                fee = params.get('site_visit_fee') or params.get('siteVisitFee')
                if fee:
                    return float(fee)
            elif metric == 'titleInsurance':
                gross = params.get('gross_amount') or params.get('grossAmount')
                rate = params.get('title_insurance_rate') or params.get('titleInsuranceRate')
                if gross and rate:
                    return float(gross) * float(rate) / 100.0
            elif metric == 'legalCosts':
                legal = params.get('legal_fees') or params.get('legalFees') or 0
                site_visit = params.get('site_visit_fee') or params.get('siteVisitFee') or 0
                gross = params.get('gross_amount') or params.get('grossAmount')
                rate = params.get('title_insurance_rate') or params.get('titleInsuranceRate') or 0
                title = float(gross) * float(rate) / 100.0 if gross and rate else 0
                return float(legal) + float(site_visit) + float(title)
        except Exception:
            return None

        return None
    
    def get_comparison_table(self):
        """Generate comparison table data"""
        if not self.scenarios:
            return []
        
        # Define key metrics to compare (mirroring calculator summary)
        key_metrics = [
            'propertyValue',
            'grossAmount',
            'startDate',
            'endDate',
            'loanTerm',
            'loanTermDays',
            'arrangementFee',
            'legalCosts',
            'siteVisitFee',
            'titleInsurance',
            'totalInterest',
            'netAdvance',
            'ltv',
            'endLTV',
            'totalNetAdvance',
            'interestSavings',
            'savingsPercentage'
        ]
        
        # Build comparison table
        comparison_data = []

        for metric in key_metrics:
            row = {
                'metric': self._format_metric_name(metric),
                'scenarios': []
            }

            for scenario in self.scenarios:
                if scenario.get('results'):
                    value = self._get_result_value(scenario['results'], metric, scenario.get('parameters'))
                    formatted_value = self._format_metric_value(metric, value)
                else:
                    value = None
                    formatted_value = 'Error' if scenario.get('error') else 'Not calculated'

                row['scenarios'].append({
                    'name': scenario['name'],
                    'value': formatted_value,
                    'raw_value': value
                })
            
            comparison_data.append(row)
        
        return comparison_data
    
    def get_best_scenario_analysis(self):
        """Analyze scenarios to identify the best options"""
        analysis = {
            'lowest_total_cost': None,
            'highest_net_advance': None,
            'lowest_interest': None,
            'best_ltv': None,
            'highest_savings': None
        }
        
        calculated_scenarios = [s for s in self.scenarios if s.get('results')]
        
        if not calculated_scenarios:
            return analysis
        
        # Find lowest total cost (interest + fees)
        min_cost = float('inf')
        for scenario in calculated_scenarios:
            results = scenario['results']
            total_cost = (
                float(self._get_result_value(results, 'totalInterest') or 0) +
                float(self._get_result_value(results, 'arrangementFee') or 0) +
                float(self._get_result_value(results, 'legalCosts') or 0) +
                float(self._get_result_value(results, 'siteVisitFee') or 0) +
                float(self._get_result_value(results, 'titleInsurance') or 0)
            )
            if total_cost < min_cost:
                min_cost = total_cost
                analysis['lowest_total_cost'] = {
                    'scenario': scenario['name'],
                    'total_cost': total_cost
                }
        
        # Find highest net advance
        max_net_advance = 0
        for scenario in calculated_scenarios:
            results = scenario['results']
            net_advance = float(self._get_result_value(results, 'totalNetAdvance') or 0)
            if net_advance > max_net_advance:
                max_net_advance = net_advance
                analysis['highest_net_advance'] = {
                    'scenario': scenario['name'],
                    'net_advance': net_advance
                }
        
        # Find lowest interest
        min_interest = float('inf')
        for scenario in calculated_scenarios:
            results = scenario['results']
            total_interest = float(self._get_result_value(results, 'totalInterest') or 0)
            if total_interest < min_interest:
                min_interest = total_interest
                analysis['lowest_interest'] = {
                    'scenario': scenario['name'],
                    'interest': total_interest
                }
        
        # Find best LTV
        min_ltv = float('inf')
        for scenario in calculated_scenarios:
            results = scenario['results']
            end_ltv = self._get_result_value(results, 'endLTV')
            if end_ltv and end_ltv != 'N/A':
                try:
                    if isinstance(end_ltv, str) and '%' in end_ltv:
                        ltv_value = float(end_ltv.replace('%', ''))
                    elif isinstance(end_ltv, (int, float)):
                        ltv_value = float(end_ltv)
                    else:
                        continue
                        
                    if ltv_value < min_ltv:
                        min_ltv = ltv_value
                        analysis['best_ltv'] = {
                            'scenario': scenario['name'],
                            'ltv': f"{ltv_value:.1f}%" if isinstance(end_ltv, (int, float)) else end_ltv
                        }
                except (ValueError, AttributeError, TypeError):
                    continue
        
        # Find highest savings
        max_savings = 0
        for scenario in calculated_scenarios:
            results = scenario['results']
            savings = self._get_result_value(results, 'interestSavings')
            if savings:
                try:
                    savings_value = float(savings) if isinstance(savings, (str, int, float)) else 0
                    if savings_value > max_savings:
                        max_savings = savings_value
                        analysis['highest_savings'] = {
                            'scenario': scenario['name'],
                            'savings': savings
                        }
                except (ValueError, TypeError):
                    continue
        
        return analysis
    
    def export_comparison(self, format='json'):
        """Export comparison data"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'scenarios': self.scenarios,
            'comparison_table': self.get_comparison_table(),
            'best_scenario_analysis': self.get_best_scenario_analysis()
        }
        
        if format == 'json':
            return json.dumps(data, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _format_metric_name(self, metric):
        """Format metric name for display"""
        name_map = {
            'propertyValue': 'Valuation',
            'grossAmount': 'Gross Amount',
            'startDate': 'Date of First Drawdown',
            'endDate': 'End Date',
            'loanTerm': 'Term (Months)',
            'loanTermDays': 'Term (Days)',
            'arrangementFee': 'Arrangement Fee',
            'legalCosts': 'Legal Costs',
            'siteVisitFee': 'Site Visit Fee',
            'titleInsurance': 'Title Insurance',
            'totalInterest': 'Interest',
            'netAdvance': 'Net Day 1 Advance',
            'ltv': 'LTV Ratio',
            'endLTV': 'End LTV',
            'totalNetAdvance': 'Total Net Advance',
            'interestSavings': 'Interest Savings',
            'savingsPercentage': 'Savings %'
        }
        return name_map.get(metric, metric)
    
    def _format_metric_value(self, metric, value):
        """Format metric value for display"""
        if value is None or value == 'N/A':
            return 'N/A'
        
        try:
            if metric in ['endLTV', 'ltv', 'savingsPercentage']:
                return f"{float(value):.2f}%"
            elif metric in ['startDate', 'endDate']:
                return str(value)
            elif metric in ['loanTerm', 'loanTermDays']:
                return f"{int(float(value))}"
            elif metric in ['propertyValue', 'grossAmount', 'netAdvance', 'totalNetAdvance', 'totalInterest',
                          'arrangementFee', 'legalCosts', 'siteVisitFee', 'titleInsurance', 'interestSavings']:
                return f"£{float(value):,.2f}"
            else:
                return str(value)
        except (ValueError, TypeError):
            return str(value)
    
    def clear_scenarios(self):
        """Clear all scenarios"""
        self.scenarios = []

# Predefined scenario templates
class ScenarioTemplates:
    @staticmethod
    def _get_complete_params(base_params):
        """Get complete parameter set with all required calculator inputs"""
        # Start with base parameters
        params = base_params.copy()
        
        # Ensure all required parameters are present with defaults
        defaults = {
            'loan_type': 'bridge',
            'currency': 'GBP',
            'property_value': 2000000,
            'amount_input_type': 'gross',
            'gross_amount_type': 'fixed',
            'gross_amount': 1000000,
            'gross_amount_percentage': 50.0,
            'net_amount': 0,
            'day1_advance': 0,
            'rate_input_type': 'annual',
            'monthly_rate': 1.0,
            'annual_rate': 12.0,
            'interest_type': 'simple',
            'loan_term': 12,
            'start_date': datetime.now().strftime('%Y-%m-%d'),
            'end_date': (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'),
            'arrangement_fee_rate': 2.0,
            'arrangement_fee_percentage': 2.0,
            'legal_fees': 1500,
            'site_visit_fee': 500,
            'title_insurance_rate': 0.01,
            'use_360_days': False,
            'payment_timing': 'advance',
            'payment_frequency': 'monthly',
            'capital_repayment': 0,
            'flexible_payment': 0,
            'repayment_option': 'none',
            'tranche_mode': 'manual',
            'tranches': []
        }
        
        # Apply defaults for missing parameters
        for key, value in defaults.items():
            if key not in params:
                params[key] = value
        
        return params
    
    @staticmethod
    def interest_rate_comparison(base_params, rates=[10, 12, 15, 18]):
        """Create scenarios comparing different interest rates"""
        scenarios = []
        for rate in rates:
            params = ScenarioTemplates._get_complete_params(base_params)
            params['annual_rate'] = rate
            params['interest_rate'] = rate
            scenarios.append({
                'name': f'{rate}% Interest Rate',
                'parameters': params
            })
        return scenarios
    
    @staticmethod
    def loan_term_comparison(base_params, terms=[6, 12, 18, 24]):
        """Create scenarios comparing different loan terms"""
        scenarios = []
        for term in terms:
            params = ScenarioTemplates._get_complete_params(base_params)
            params['loan_term'] = term
            # Update end date based on loan term
            start_date = datetime.strptime(params['start_date'], '%Y-%m-%d')
            end_date = start_date + timedelta(days=term * 30)  # Approximate
            params['end_date'] = end_date.strftime('%Y-%m-%d')
            scenarios.append({
                'name': f'{term} Month Term',
                'parameters': params
            })
        return scenarios
    
    @staticmethod
    def repayment_option_comparison(base_params):
        """Create scenarios comparing different repayment options"""
        loan_type = base_params.get('loan_type', 'bridge')
        scenarios = []
        
        if loan_type == 'bridge':
            options = [
                ('none', 'Retained Interest'),
                ('service_only', 'Interest Only'),
                ('service_and_capital', 'Service + Capital'),
                ('flexible_payment', 'Flexible Payment')
            ]
        elif loan_type == 'term':
            options = [
                ('none', 'Retained Interest'),
                ('service_only', 'Interest Only'),
                ('service_and_capital', 'Amortizing')
            ]
        else:  # development
            options = [
                ('none', 'Retained Interest'),
                ('interest_only', 'Interest Only'),
                ('capital_interest', 'Capital + Interest')
            ]
        
        for option_key, option_name in options:
            params = ScenarioTemplates._get_complete_params(base_params)
            params['repayment_option'] = option_key
            
            # Add specific parameters for certain repayment types
            if option_key == 'flexible_payment':
                params['flexible_payment'] = 20000
            elif option_key == 'service_and_capital':
                params['capital_repayment'] = 50000
            
            scenarios.append({
                'name': option_name,
                'parameters': params
            })
        
        return scenarios
    
    @staticmethod
    def loan_amount_comparison(base_params, amounts=[500000, 750000, 1000000, 1500000]):
        """Create scenarios comparing different loan amounts"""
        scenarios = []
        amount_input_type = base_params.get('amount_input_type', 'gross')
        
        for amount in amounts:
            params = ScenarioTemplates._get_complete_params(base_params)
            
            if amount_input_type == 'gross':
                params['gross_amount'] = amount
            else:
                params['net_amount'] = amount
            
            scenarios.append({
                'name': f'£{amount:,} Loan',
                'parameters': params
            })
        return scenarios

    @staticmethod
    def interest_type_comparison(
        base_params,
        interest_types=['simple', 'compound_daily', 'compound_monthly', 'compound_quarterly']
    ):
        """Create scenarios comparing different interest calculation methods"""
        scenarios = []
        name_map = {
            'simple': 'Simple Interest',
            'compound_daily': 'Compound Daily',
            'compound_monthly': 'Compound Monthly',
            'compound_quarterly': 'Compound Quarterly'
        }

        for interest_type in interest_types:
            params = ScenarioTemplates._get_complete_params(base_params)
            params['interest_type'] = interest_type
            scenarios.append({
                'name': name_map.get(interest_type, interest_type.replace('_', ' ').title()),
                'parameters': params
            })

        return scenarios

# Flask integration helper
def create_scenario_comparison_from_request(request_data):
    """Create scenario comparison from Flask request data"""
    comparison = ScenarioComparison()
    
    scenarios_data = request_data.get('scenarios', [])
    for scenario_data in scenarios_data:
        comparison.add_scenario(
            scenario_data.get('name', 'Unnamed Scenario'),
            scenario_data.get('parameters', {})
        )
    
    return comparison
