import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parent
CALCULATOR_JS = PROJECT_ROOT / "static" / "js" / "calculator.js"


def _run_node_script(tz: str) -> dict:
    env = os.environ.copy()
    env["TZ"] = tz

    script = f"""
const fs = require('fs');
const vm = require('vm');
const path = require('path');

const noop = function(){{}};

const makeElement = (initial = {{}}) => Object.assign({{
    value: '',
    textContent: '',
    innerHTML: '',
    style: {{}},
    appendChild: noop,
    remove: noop,
    setAttribute: noop,
    getAttribute: () => null,
    addEventListener: noop,
    removeEventListener: noop,
    focus: noop,
    querySelector: () => null,
    querySelectorAll: () => [],
}}, initial);

const elements = {{}};
const trancheContainer = makeElement({{ innerHTML: '' }});

const consoleStub = {{
    log: noop,
    warn: noop,
    error: noop,
    info: noop,
}};

elements['autoTotalAmount'] = makeElement({{ value: '100000' }});
elements['autoStartDate'] = makeElement({{ value: '2024-01-01' }});
elements['autoLoanPeriod'] = makeElement({{ value: '12' }});
elements['autoInterestRate'] = makeElement({{ value: '7' }});
elements['autoTrancheCount'] = makeElement({{ value: '5' }});
elements['trancheCount'] = makeElement({{ textContent: '0' }});
elements['manual_tranches'] = makeElement({{ checked: false }});
elements['tranchesContainer'] = trancheContainer;

const documentStub = {{
    addEventListener: noop,
    removeEventListener: noop,
    getElementById: (id) => elements[id] || null,
    querySelector: () => null,
    querySelectorAll: () => [],
    createElement: () => makeElement(),
    body: {{
        appendChild: noop,
        removeChild: noop,
    }},
}};

const context = {{
    window: {{}},
    document: documentStub,
    console: consoleStub,
    setTimeout: noop,
    clearTimeout: noop,
}};
context.window.window = context.window;
context.window.document = documentStub;
context.window.addEventListener = noop;
context.window.removeEventListener = noop;
context.document = documentStub;
context.Novellus = {{ forms: {{ validate: () => true }} }};
context.window.Novellus = context.Novellus;
context.global = context;
context.globalThis = context;

vm.createContext(context);
const code = fs.readFileSync({json.dumps(str(CALCULATOR_JS))}, 'utf8');
vm.runInContext(code, context);
vm.runInContext('globalThis.__loanCalculatorClass = LoanCalculator;', context);

const LoanCalculator = context.__loanCalculatorClass || context.window.LoanCalculator;
if (!LoanCalculator || typeof LoanCalculator.formatDateForStorage !== 'function') {{
    throw new Error('LoanCalculator.formatDateForStorage not available');
}}

const generatedTranches = [];
const testCalculator = {{
    clearTranches: () => {{ trancheContainer.innerHTML = ''; }},
    createTrancheItem: (number, amount, date, rate, label) => {{
        generatedTranches.push({{
            number,
            amount,
            date,
            rate,
            label,
        }});
    }},
    toggleTrancheMode: noop,
}};

LoanCalculator.prototype.generateTranches.call(testCalculator);

const results = {{
    fromUtc: LoanCalculator.formatDateForStorage(new Date(Date.UTC(2024, 3, 1))),
    fromLocal: LoanCalculator.formatDateForStorage(new Date('2024-04-01T00:00:00')),
    fromString: LoanCalculator.formatDateForStorage('2024-04-01'),
    trancheDates: generatedTranches.map((t) => t.date),
}};

process.stdout.write(JSON.stringify(results));
"""

    try:
        completed = subprocess.run(
            ["node", "-e", script],
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
    except FileNotFoundError:
        pytest.skip("Node.js runtime is required for tranche date regression test")
    except subprocess.CalledProcessError as exc:  # pragma: no cover - debug output on failure
        raise AssertionError(f"Node script failed: {exc.stderr}") from exc

    return json.loads(completed.stdout or "{}")


@pytest.mark.parametrize("timezone", ["UTC", "America/Los_Angeles", "Pacific/Kiritimati"])
def test_tranche_date_rendering_stable_across_timezones(timezone):
    results = _run_node_script(timezone)

    assert results["fromUtc"] == "2024-04-01"
    assert results["fromLocal"] == "2024-04-01"
    assert results["fromString"] == "2024-04-01"

    tranche_dates = results.get("trancheDates", [])
    assert len(tranche_dates) == 5

    parsed_dates = [datetime.strptime(date_str, "%Y-%m-%d") for date_str in tranche_dates]
    month_positions = [dt.year * 12 + dt.month for dt in parsed_dates]

    for previous, current in zip(month_positions, month_positions[1:]):
        assert current - previous == 1, (
            f"Expected tranche dates to progress monthly, got {tranche_dates}"
        )
