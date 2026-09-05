# 🧪 SauceDemo Playwright Test Automation Framework

A production-grade Playwright test automation framework for SauceDemo.com.

## Quick Start
```bash
pip3 install playwright pytest pytest-html
playwright install chromium
pytest tests/ -v --html=reports/report.html --self-contained-html
```