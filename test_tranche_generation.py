import types
import sys
from calculations import LoanCalculator

# Stub numpy.linspace and isscalar to avoid external dependency
sys.modules['numpy'] = types.SimpleNamespace(
    linspace=lambda start, stop, num: [start + (stop - start) * i / (num - 1) for i in range(num)],
    isscalar=lambda obj: isinstance(obj, (int, float)),
    bool_=bool,
    ndarray=list
)

# Stub dateutil.relativedelta with minimal month addition
relativedelta_module = types.ModuleType('relativedelta')

class relativedelta:
    def __init__(self, months=0):
        self.months = months

    def __radd__(self, other):
        # Add months to a datetime object
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

def test_tranche_breakdown_matches_input_count():
    calculator = LoanCalculator()
    params = {
        'day1_advance': 100000,
        'legal_fees': 0,
        'annual_rate': 12.0,
        'arrangement_fee_rate': 2.0,
        'title_insurance_rate': 0.01,
        'site_visit_fee': 0,
        'net_amount': 200000,
        'loan_term': 12,
        'start_date': '2025-01-01',
        # Create 10 tranches from month 2 onwards
        'tranches': [{'amount': 10000, 'month': m} for m in range(2, 12)]
    }
    result = calculator.calculate_development2_loan(params)
    additional = [t for t in result['tranche_breakdown'] if t['tranche_number'] > 1]
    assert len(additional) == 10
    assert additional[0]['release_date'] == '2025-02-01'
    assert additional[-1]['release_date'] == '2025-11-01'


def test_auto_tranches_start_from_second_month():
    calculator = LoanCalculator()
    params = {
        'day1_advance': 100000,
        'legal_fees': 0,
        'annual_rate': 12.0,
        'arrangement_fee_rate': 2.0,
        'title_insurance_rate': 0.01,
        'site_visit_fee': 0,
        'net_amount': 200000,
        'loan_term': 12,
        'start_date': '2025-01-01'
    }
    result = calculator.calculate_development2_loan(params)
    auto_tranches = [t for t in result['tranche_breakdown'] if t['tranche_number'] > 1]
    assert auto_tranches[0]['release_date'] == '2025-02-01'
    assert auto_tranches[-1]['release_date'] == '2025-12-01'
