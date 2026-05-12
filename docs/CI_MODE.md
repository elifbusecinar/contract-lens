# ContractLens — CI mode

ContractLens can fail a CI job when contract drift exceeds a configurable risk threshold **after** the normal audit completes and the Markdown report is written.

## CLI

```bash
python -m contractlens.main \
  --feature "Create Project + Upload File" \
  --root path/to/repo \
  --ci \
  --fail-on High \
  --verbose
```

| Flag | Meaning |
| --- | --- |
| `--ci` | After the workflow, evaluate mismatches and set process exit code. |
| `--fail-on High` | **Default.** Exit **1** if any mismatch has risk **High** (or stricter ordering). |
| `--fail-on Medium` | Exit **1** if any mismatch is **High** or **Medium**. |
| `--fail-on Low` | Exit **1** if any mismatch is **High**, **Medium**, or **Low**. |

**Exit codes**

| Code | When |
| --- | --- |
| `0` | No workflow errors and CI gate passed (or `--ci` not used). |
| `1` | Workflow errors, **or** `--ci` and at least one mismatch meets/exceeds `--fail-on`. |

The report path is printed before the `[CI]` summary. **Exit code 1 from `--ci` is expected** when the sample project or your repo still has High-severity drift.

## Risk ordering

Deterministic ordering used by the gate: **High > Medium > Low > Unknown**.

`Unknown` mismatches do **not** fail a `--fail-on Low` gate (they rank below Low). This matches “fail only on labeled severities”; adjust if you treat Unknown as blocking.

## MCP: `evaluate_ci_gate`

Input:

```json
{
  "mismatches": [
    { "area": "path", "risk": "High", "frontend_expects": "...", "backend_provides": "...", "suggestion": "..." }
  ],
  "fail_on": "High"
}
```

Output:

```json
{
  "passed": false,
  "exit_code": 1,
  "summary": {
    "counts_by_risk": { "High": 1, "Medium": 0, "Low": 0, "Unknown": 0 },
    "fail_on": "High",
    "mismatch_total": 1
  }
}
```

Use this to mirror CI logic in an agent or a thin wrapper without re-running the full workflow.

## GitHub Actions example

No GitHub App or PAT integration is required — run ContractLens as a normal step.

```yaml
name: ContractLens CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  contractlens:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install ContractLens
        run: pip install -r requirements.txt

      - name: Audit contracts (fail on High drift)
        run: |
          python -m contractlens.main \
            --feature "Backend vs Frontend" \
            --root . \
            --ci \
            --fail-on High \
            --verbose

      - name: Upload report artifact (optional)
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: contractlens-report
          path: contractlens-reports/*.md
```

Notes:

- Use **`if: always()`** on upload steps if you want the Markdown artifact even when the gate fails.
- Tune `--root` to the subtree you audit (monorepo-friendly).
- **`continue-on-error: true`** on the audit step is an alternative if you only want reports without failing the job.

## Limitations

- CI mode inspects **mismatch rows only**; it does not re-scan or reinterpret findings.
- **`Unknown` severity** is excluded from Low/Medium/High thresholds as described above.
- **`generate_contract_report`** MCP tool does not yet expose `--ci`; invoke `evaluate_ci_gate` on returned mismatches or call the CLI in CI.
