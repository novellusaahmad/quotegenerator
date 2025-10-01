import json
import os
import subprocess
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
const documentStub = {{
    addEventListener: noop,
    removeEventListener: noop,
    getElementById: () => null,
    querySelector: () => null,
    querySelectorAll: () => [],
    createElement: () => ({{
        style: {{}},
        appendChild: noop,
        remove: noop,
        setAttribute: noop,
        getContext: () => null,
    }}),
    body: {{
        appendChild: noop,
        removeChild: noop,
    }},
}};

const context = {{
    window: {{}},
    document: documentStub,
    console: console,
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

const results = {{
    fromUtc: LoanCalculator.formatDateForStorage(new Date(Date.UTC(2024, 3, 1))),
    fromLocal: LoanCalculator.formatDateForStorage(new Date('2024-04-01T00:00:00')),
    fromString: LoanCalculator.formatDateForStorage('2024-04-01'),
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
