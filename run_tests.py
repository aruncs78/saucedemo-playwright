"""
Main Test Runner for SauceDemo Playwright Automation Framework.
"""
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
from generate_dashboard import generate_dashboard


def run_command(cmd: str, cwd: str = None) -> subprocess.CompletedProcess:
    """Run a shell command."""
    print(f"Executing: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd, timeout=300)
    return result


def main():
    """Main test runner."""
    base_dir = Path(__file__).parent
    os.chdir(base_dir)

    print("=" * 70)
    print(" SAUCEDEMO PLAYWRIGHT TEST AUTOMATION FRAMEWORK")
    print("=" * 70)
    print(f" Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    reports_dir = base_dir / "reports"
    screenshots_dir = reports_dir / "screenshots"
    reports_dir.mkdir(parents=True, exist_ok=True)
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    # Verify dependencies
    result = run_command("python -c 'from playwright.sync_api import sync_playwright' ")
    if result.returncode != 0:
        print("Installing playwright...")
        run_command("pip3 install playwright --break-system-packages")

    run_command("python -c 'import pytest_html' ")

    print("=" * 70)
    print(" RUNNING TEST SUITE")
    print("=" * 70)
    print()

    report_html = str(reports_dir / "report.html")
    pytest_cmd = f"pytest tests/test_login_scenarios.py -v --tb=long --maxfail=5 --html={report_html} --self-contained-html --capture=no"
    result = run_command(pytest_cmd, cwd=str(base_dir))

    print()
    print("=" * 70)
    print(" GENERATING DASHBOARD")
    print("=" * 70)
    print()

    dashboard = generate_dashboard(output_file=str(reports_dir / "dashboard.html"))

    print()
    print("=" * 70)
    print(" COMPLETE")
    print("=" * 70)
    print(f" Dashboard: {dashboard}")
    print(f" Report: {report_html}")
    print(f" Screenshots: {screenshots_dir}/")


if __name__ == "__main__":
    main()
