import json
import re
import subprocess
from pathlib import Path

def _run_build_edit_params(loan_obj):
    content = Path('templates/loan_history.html').read_text()
    # Extract the body of buildEditParams function
    match = re.search(r'buildEditParams\(loan\)\s*{([\s\S]*?)}\s*showState', content)
    assert match, "buildEditParams function not found"
    body = match.group(1)
    node_script = f"""
const loan = {json.dumps(loan_obj)};
function buildEditParams(loan) {{{body}}}
const result = buildEditParams(loan);
console.log(JSON.stringify(result));
"""
    output = subprocess.check_output(['node', '-e', node_script], text=True)
    last_line = output.strip().splitlines()[-1]
    return json.loads(last_line)

def test_build_edit_params_includes_development2_tranches():
    loan_obj = {
        'loan_type': 'development2',
        'tranches': [
            {'amount': '10000', 'date': '2024-01-01', 'rate': '10', 'description': 'Phase 1'},
            {'amount': '20000', 'date': '2024-06-01', 'rate': '11', 'description': 'Phase 2'},
        ]
    }
    result = _run_build_edit_params(loan_obj)
    assert result['tranche_amounts[0]'] == '10000'
    assert result['tranche_dates[0]'] == '2024-01-01'
    assert result['tranche_rates[0]'] == '10'
    assert result['tranche_descriptions[0]'] == 'Phase 1'
    assert result['tranche_amounts[1]'] == '20000'
    assert result['tranche_dates[1]'] == '2024-06-01'
    assert result['tranche_rates[1]'] == '11'
    assert result['tranche_descriptions[1]'] == 'Phase 2'


def test_build_edit_params_rounds_interest_rate():
    loan_obj = {
        'interest_rate': 9.9996
    }
    result = _run_build_edit_params(loan_obj)
    assert result['annual_rate'] == '10'
