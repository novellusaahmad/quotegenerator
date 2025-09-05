import json
import re
import subprocess
from pathlib import Path

def _run_populate_tranche_data(params):
    content = Path('templates/calculator.html').read_text()
    # Extract function body
    match = re.search(r'function populateTrancheData\(params\) \{([\s\S]*?)\}\n\s*// Cancel edit', content)
    assert match, 'populateTrancheData function not found'
    body = match.group(1)
    params_list = list(params.items())
    node_script = f"""
const params = new URLSearchParams({json.dumps(params_list)});
let created = [];
let container = {{ innerHTML: 'existing' }};
global.window = {{loanCalculator: {{createTrancheItem: (n,a,d,r,desc) => created.push({{number:n, amount:a, date:d, rate:r, description:desc}})}}}};
global.document = {{getElementById: id => id === 'tranchesContainer' ? container : null}};
function populateTrancheData(params) {{{body}}}
populateTrancheData(params);
console.log(JSON.stringify({{"created": created, "innerHTML": container.innerHTML}}));
"""
    output = subprocess.check_output(['node', '-e', node_script], text=True)
    return json.loads(output.strip().splitlines()[-1])

def test_populate_tranche_data_creates_tranches():
    params = {
        'loan_type': 'development2',
        'tranche_amounts[0]': '10000',
        'tranche_dates[0]': '2024-01-01',
        'tranche_rates[0]': '10',
        'tranche_descriptions[0]': 'Phase 1',
        'tranche_amounts[1]': '20000',
        'tranche_dates[1]': '2024-06-01',
        'tranche_rates[1]': '11',
        'tranche_descriptions[1]': 'Phase 2',
    }
    result = _run_populate_tranche_data(params)
    assert result['innerHTML'] == ''
    assert result['created'] == [
        {'number': 1, 'amount': 10000.0, 'date': '2024-01-01', 'rate': 10.0, 'description': 'Phase 1'},
        {'number': 2, 'amount': 20000.0, 'date': '2024-06-01', 'rate': 11.0, 'description': 'Phase 2'},
    ]
