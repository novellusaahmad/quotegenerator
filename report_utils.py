from typing import Any, Dict, List
from calculations import LoanCalculator


def generate_report_schedule(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate a detailed payment schedule for report output.

    Service + Capital and Flexible Payment reports should present a payment
    schedule identical to the Capital Payment Only option. This helper
    provides that behaviour while leaving standard calculations untouched.
    """
    calc = LoanCalculator()
    repayment_option = params.get('repayment_option')
    if repayment_option in ('service_and_capital', 'flexible_payment'):
        cap_params = params.copy()
        cap_params['repayment_option'] = 'capital_payment_only'
        if repayment_option == 'flexible_payment' and 'capital_repayment' not in cap_params:
            cap_params['capital_repayment'] = params.get('flexible_payment', 0)
        return calc.calculate_bridge_loan(cap_params).get('detailed_payment_schedule', [])
    return calc.calculate_bridge_loan(params).get('detailed_payment_schedule', [])
