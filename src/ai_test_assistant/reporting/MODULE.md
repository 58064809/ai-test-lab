# Allure reporting

This package handles the small, controlled Allure reporting boundary.

## Test report chain

- Runtime supports explicit `--run-test-report [TARGET]`.
- The chain is fixed: `pytest` -> `allure generate` -> Allure summary read.
- It only combines existing controlled adapters: `PytestRunner`, `AllureReportGenerator`, and `AllureReportReader`.
- Pytest may only append the fixed `--alluredir=allure-results` argument.
- Arbitrary pytest arguments and arbitrary Allure arguments remain blocked.
- This is the Allure workflow closure point; avoid continuing to split smaller Allure tasks unless the boundary changes.

## Read-only summary

- Reads only repository-relative report directories.
- Defaults to `allure-report`.
- Reads `widgets/summary.json` first.
- Optionally reads `widgets/duration.json`, `widgets/categories.json`, and `widgets/suites.json`.
- Does not persist complete widget JSON into memory.

## Controlled generation

- Uses official Allure CLI only.
- Runs the fixed command shape: `allure generate <results_dir> -o <report_dir> --clean`.
- Defaults to `allure-results` and `allure-report`.
- Uses `subprocess.run` with an args list and `shell=False`.
- Does not support `allure serve`.
- Does not support arbitrary Allure arguments.
- Does not auto-install Allure CLI.
- Windows users must install Allure CLI themselves and ensure `allure --version` works.

## Shared boundary

- Only repository-relative paths are accepted.
- Absolute paths, `..`, glob patterns, and sensitive path names are blocked.
- Does not open shell, filesystem write, or external network access.
