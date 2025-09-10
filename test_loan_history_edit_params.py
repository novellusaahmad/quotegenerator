import json
import re
import subprocess
from pathlib import Path


def _run_edit_loan(current_id, loans):
    content = Path('templates/loan_history.html').read_text()
    assert 'buildEditParams' not in content
    match = re.search(r'editLoan\(\)\s*{([\s\S]*?)\n\s*}\s*\n\s*editLoanFromTable', content)
    assert match, "editLoan function not found"
    body = match.group(1)
    node_script = f"""
const window = {{ notifications: {{ error: ()=>{{}} }}, location: {{ href: '' }} }};
function alert(){{}};
const loanHistory = {{
    currentLoanId: {current_id},
    loans: {json.dumps(loans)}
}};
loanHistory.editLoan = function() {{{body}}};
loanHistory.editLoan();
console.log(window.location.href);
"""
    output = subprocess.check_output(['node', '-e', node_script], text=True)
    return output.strip().splitlines()[-1]


def test_edit_loan_redirects_with_basic_params():
    url = _run_edit_loan(5, [{'id': 5, 'loan_name': 'Test Loan'}])
    assert url == "/calculator?edit=true&loanId=5&loanName=Test+Loan"
