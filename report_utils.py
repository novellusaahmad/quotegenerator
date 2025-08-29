from typing import Any, Dict, List
from calculations import LoanCalculator


def generate_report_schedule(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate a detailed payment schedule for report output.


    Capital Payment Only already produces the desired report format. For
    Service + Capital and Flexible Payment the underlying engine yields a
    different schedule layout, so this helper re-runs the calculation using
    the Capital Payment Only breakdown to ensure all three repayment options
    share an identical structure in generated reports while leaving standard
    calculations untouched.

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
