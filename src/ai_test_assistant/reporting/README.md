# Allure report read-only summary

This package reads summary metadata from an existing Allure HTML report directory.

Current boundary:

- Reads only repository-relative report directories.
- Defaults to `allure-report`.
- Reads `widgets/summary.json` first.
- Optionally reads `widgets/duration.json`, `widgets/categories.json`, and `widgets/suites.json`.
- Does not generate Allure HTML.
- Does not execute Allure CLI.
- Does not open shell, filesystem write, or external network access.
- Does not persist complete widget JSON into memory.
