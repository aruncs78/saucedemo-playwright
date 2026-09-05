# SAUCEDEMO PLAYWRIGHT TEST AUTOMATION FRAMEWORK

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-Latest-green.svg)](https://playwright.dev/)
[![pytest](https://img.shields.io/badge/pytest-Latest-purple.svg)](https://docs.pytest.org/)

## Overview

A production-grade **Playwright test automation framework** for [SauceDemo.com](https://www.saucedemo.com) with **30+ comprehensive login test scenarios**.

## Features

- **Page Object Model (POM)** architecture
- **30+ test scenarios** covering all login edge cases
- **Beautiful HTML dashboard** with pass/fail statistics and screenshots
- **Security testing** (SQL injection, XSS prevention)
- **Parameterized tests** for data-driven testing
- **Modular structure** for easy extension

## Project Structure

```
saucedemo-playwright/
├── tests/
│   ├── conftest.py              # Pytest fixtures & hooks
│   ├── test_login_scenarios.py  # All test scenarios (30+ tests)
│   ├── pages/
│   │   ├── base_page.py         # Base page with common methods
│   │   ├── login_page.py        # Login page object
│   │   └── products_page.py     # Products/inventory page object
│   ├── utils/
│   │   └── helpers.py           # Utility functions
│   └── data/                    # Test data
├── reports/                     # Test results & screenshots
├── pytest.ini                   # Pytest configuration
├── generate_dashboard.py        # Dashboard generator
├── run_tests.py                 # Main test runner
└── README.md
```

## Quick Start

```bash
# Install dependencies
pip3 install playwright pytest pytest-html
playwright install chromium

# Run all tests
pytest tests/ -v --html=reports/report.html --self-contained-html

# Run with headed browser
pytest tests/ --headed

# Run smoke tests only
pytest tests/ -m smoke

# Run specific category
pytest tests/test_login_scenarios.py -v -k "SuccessfulLogin"
```

## Test Scenarios (30+)

### Successful Login (TC001-005)
- Login with standard_user, problem_user, performance_glitch_user
- Verify products page loads with 6 products
- Verify URL and title changes
- Cross-user verification

### Invalid Username (TC006-007)
- Multiple invalid usernames
- Error clears on new input

### Invalid Password (TC008-009)
- Multiple invalid passwords
- Username preserved after failed login

### Both Invalid (TC010-011)
- Both fields wrong
- Error text verification

### Empty Fields (TC012-013)
- Empty username/password combos
- Click login with no input

### Security (TC014-016)
- SQL injection attempts
- XSS attempts

### Edge Cases (TC017-030)
- Long strings (500/1000 chars)
- Whitespace inputs
- Post-login verification
- Logout functionality
- Case sensitivity
- Rapid login/logout cycles
- Direct URL access
- Multiple consecutive failures

## Architecture

### Page Object Model
```
BasePage (base_page.py)
├── LoginPage (login_page.py)    → Login interactions
└── ProductsPage (products_page.py) → Post-login interactions
```

## Dashboard

The dashboard provides:
- Summary statistics (total, passed, failed, pass rate)
- Visual progress bar
- Category-grouped results
- Screenshot links for failures
- Error details

Open `reports/dashboard.html` after running tests.

## License

MIT License
