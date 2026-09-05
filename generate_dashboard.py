"""
Results Dashboard Generator for SauceDemo Playwright Tests.
Generates a beautiful HTML dashboard with test results, screenshots, and statistics.
"""
import os
import re
from pathlib import Path
from datetime import datetime
from html import escape

BASE_DIR = Path(__file__).parent
REPORTS_DIR = BASE_DIR / "reports"
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"


def parse_pytest_output(output: str) -> list:
    """Parse pytest output to extract test results."""
    results = []
    lines = output.split('\n')
    current_test = None
    current_status = None
    current_error = None

    for line in lines:
        match = re.search(r'(tests/.*\.py::\w+|::\w+)\s+(PASSED|FAILED|SKIPPED|ERROR)', line)
        if match:
            if current_test and current_status:
                results.append({"test": current_test, "status": current_status, "error": current_error})
            current_test = match.group(1).replace("tests/", "").replace(".py::", "/")
            current_status = match.group(2)
            current_error = None
        elif current_status == "FAILED" and line.strip().startswith("E "):
            if current_error is None:
                current_error = ""
            current_error += line.strip()[2:] + "\n"
        elif current_error is not None and line.strip() and not line.startswith("="):
            current_error += line.strip() + "\n"

    if current_test and current_status:
        results.append({"test": current_test, "status": current_status, "error": current_error})
    return results


def get_screenshot_path(test_name: str) -> str:
    """Find screenshot for a test."""
    if not SCREENSHOTS_DIR.exists():
        return None
    safe_name = test_name.replace("/", "_").replace("::", "_")
    for f in SCREENSHOTS_DIR.iterdir():
        if safe_name.replace("test_", "") in f.name or safe_name in f.name:
            return str(f.relative_to(BASE_DIR))
    return None


def generate_dashboard(results_file: str = None, output_file: str = None):
    """Generate the HTML dashboard."""
    if output_file is None:
        output_file = str(REPORTS_DIR / "dashboard.html")

    results = []
    total = passed = failed = skipped = 0

    if results_file and os.path.exists(results_file):
        with open(results_file, 'r') as f:
            output = f.read()
        results = parse_pytest_output(output)

    for r in results:
        total += 1
        if r["status"] == "PASSED": passed += 1
        elif r["status"] == "FAILED": failed += 1
        elif r["status"] in ("SKIPPED", "ERROR"): skipped += 1

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pass_rate = (passed / total * 100) if total > 0 else 0
    fail_rate = (failed / total * 100) if total > 0 else 0

    # Group by category
    categories = {}
    for r in results:
        cat = "General Tests"
        name = r["test"]
        if "SuccessfulLogin" in name or "TC001" in name or "TC002" in name:
            cat = "Successful Login"
        elif "InvalidUsername" in name or "TC006" in name:
            cat = "Invalid Username"
        elif "InvalidPassword" in name or "TC008" in name:
            cat = "Invalid Password"
        elif "BothInvalid" in name or "TC010" in name:
            cat = "Both Invalid Credentials"
        elif "EmptyFields" in name or "TC012" in name:
            cat = "Empty Fields"
        elif "SpecialCharacters" in name or "TC014" in name:
            cat = "Special Characters (Security)"
        elif "LongStrings" in name or "TC017" in name:
            cat = "Long Strings"
        elif "Whitespace" in name or "TC018" in name:
            cat = "Whitespace"
        elif "PostLogin" in name or "TC019" in name:
            cat = "Post-Login Verification"
        elif "Logout" in name or "TC021" in name:
            cat = "Logout"
        elif "CrossBrowser" in name or "TC023" in name:
            cat = "Cross-Browser"
        elif "EdgeCases" in name or "TC024" in name:
            cat = "Edge Cases"
        categories.setdefault(cat, []).append(r)

    # Build dashboard HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>SauceDemo Playwright Test Dashboard</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif; background:linear-gradient(135deg,#0f0c29,#302b63,#24243e); color:#e0e0e0; min-height:100vh; padding:20px; }}
.container {{ max-width:1400px; margin:0 auto; }}
.header {{ text-align:center; padding:30px 20px; background:rgba(255,255,255,0.05); border-radius:16px; margin-bottom:30px; border:1px solid rgba(255,255,255,0.1); }}
.header h1 {{ font-size:2.5em; background:linear-gradient(90deg,#00d2ff,#3a7bd5,#00d2ff); background-size:200% auto; -webkit-background-clip:text; -webkit-text-fill-color:transparent; animation:shimmer 3s linear infinite; margin-bottom:10px; }}
@keyframes shimmer {{ to {{ background-position:200% center; }} }}
.subtitle {{ color:#888; font-size:1.1em; }}
.timestamp {{ color:#666; font-size:0.9em; margin-top:8px; }}
.stats-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:20px; margin-bottom:30px; }}
.stat-card {{ background:rgba(255,255,255,0.05); border-radius:12px; padding:25px; text-align:center; border:1px solid rgba(255,255,255,0.1); transition:transform 0.3s; }}
.stat-card:hover {{ transform:translateY(-5px); }}
.stat-card .number {{ font-size:3em; font-weight:700; margin:10px 0; }}
.stat-card .label {{ font-size:0.95em; text-transform:uppercase; letter-spacing:2px; opacity:0.7; }}
.stat-card.total .number {{ color:#4fc3f7; }}
.stat-card.passed .number {{ color:#66bb6a; }}
.stat-card.failed .number {{ color:#ef5350; }}
.stat-card.rate .number {{ color:#ffd54f; }}
.progress-bar {{ width:100%; height:12px; background:rgba(255,255,255,0.1); border-radius:6px; overflow:hidden; margin-top:15px; }}
.progress-bar .fill {{ height:100%; border-radius:6px; background:linear-gradient(90deg,#43a047,#66bb6a); transition:width 1s; }}
.section-title {{ font-size:1.5em; margin:30px 0 20px; padding-bottom:10px; border-bottom:2px solid rgba(255,255,255,0.1); }}
.results-table {{ width:100%; border-collapse:collapse; background:rgba(255,255,255,0.03); border-radius:12px; overflow:hidden; }}
.results-table thead {{ background:rgba(255,255,255,0.08); }}
.results-table th {{ padding:15px 20px; text-align:left; font-weight:600; text-transform:uppercase; letter-spacing:1px; font-size:0.85em; color:#aaa; }}
.results-table td {{ padding:12px 20px; border-top:1px solid rgba(255,255,255,0.05); }}
.results-table tr:hover {{ background:rgba(255,255,255,0.03); }}
.badge {{ display:inline-block; padding:4px 12px; border-radius:20px; font-size:0.8em; font-weight:600; text-transform:uppercase; letter-spacing:1px; }}
.badge.passed {{ background:rgba(102,187,106,0.15); color:#66bb6a; border:1px solid rgba(102,187,106,0.3); }}
.badge.failed {{ background:rgba(239,83,80,0.15); color:#ef5350; border:1px solid rgba(239,83,80,0.3); }}
.badge.skipped {{ background:rgba(255,213,79,0.15); color:#ffd54f; border:1px solid rgba(255,213,79,0.3); }}
.screenshot-link {{ color:#4fc3f7; text-decoration:none; }}
.screenshot-link:hover {{ color:#81d4fa; text-decoration:underline; }}
.error-text {{ color:#ef5350; font-size:0.85em; max-width:400px; white-space:pre-wrap; word-break:break-word; }}
.footer {{ text-align:center; margin-top:40px; padding:20px; color:#555; font-size:0.85em; }}
.overall-result {{ text-align:center; padding:20px; margin:20px 0; border-radius:12px; font-size:1.3em; font-weight:600; }}
.overall-result.pass {{ background:rgba(102,187,106,0.1); border:1px solid rgba(102,187,106,0.3); color:#66bb6a; }}
.overall-result.fail {{ background:rgba(239,83,80,0.1); border:1px solid rgba(239,83,80,0.3); color:#ef5350; }}
.category {{ background:rgba(255,255,255,0.02); border-radius:12px; margin-bottom:20px; border:1px solid rgba(255,255,255,0.05); overflow:hidden; }}
.category-header {{ padding:15px 20px; background:rgba(255,255,255,0.05); font-weight:600; font-size:1.1em; }}
.category-body {{ padding:10px 20px 15px; }}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>G SauceDemo Test Dashboard</h1>
<p class="subtitle">Playwright E2E Automation Test Results</p>
<p class="timestamp">Generated: {escape(timestamp)}</p>
</div>
<div class="stats-grid">
<div class="stat-card total"><div class="label">Total Tests</div><div class="number">{total}</div></div>
<div class="stat-card passed"><div class="label">Passed</div><div class="number">{passed}</div></div>
<div class="stat-card failed"><div class="label">Failed</div><div class="number">{failed}</div></div>
<div class="stat-card skipped"><div class="label">Skipped</div><div class="number">{skipped}</div></div>
<div class="stat-card rate"><div class="label">Pass Rate</div><div class="number">{pass_rate:.1f}%</div><div class="progress-bar"><div class="fill" style="width:{pass_rate}%"></div></div></div>
</div>
<div class="overall-result {'pass' if failed==0 else 'fail'}">{'ALL TESTS PASSED!' if failed==0 else 'SOME TESTS FAILED'}</div>
<h2 class="section-title">Test Results</h2>
"""

    for cat, cat_results in categories.items():
        cat_passed = sum(1 for r in cat_results if r["status"] == "PASSED")
        cat_failed = sum(1 for r in cat_results if r["status"] == "FAILED")
        html += f"""<div class="category"><div class="category-header">{escape(cat)} — {len(cat_results)} tests ({cat_passed} passed, {cat_failed} failed)</div><div class="category-body"><table class="results-table"><thead><tr><th>#</th><th>Test Name</th><th>Status</th><th>Screenshot</th><th>Details</th></tr></thead><tbody>"""
        for i, r in enumerate(cat_results, 1):
            screenshot = get_screenshot_path(r["test"])
            s_cell = f'<a href="{escape(screenshot)}" target="_blank" class="screenshot-link">View</a>' if screenshot else 'N/A'
            e_cell = f'<div class="error-text">{escape(str(r.get("error", ""))[:300])}</div>' if r.get("error") else ""
            html += f'<tr><td>{i}</td><td>{escape(r["test"])}</td><td><span class="badge {r["status"].lower()}">{r["status"]}</span></td><td>{s_cell}</td><td>{e_cell}</td></tr>'
        html += "</tbody></table></div></div>"

    html += f"""<div class="footer"><p>SauceDemo Playwright Test Automation Framework v1.0</p><p>Built with Playwright + pytest</p></div></div></body></html>"""

    with open(output_file, 'w') as f:
        f.write(html)
    print(f"Dashboard generated: {output_file}")
    return output_file


if __name__ == "__main__":
    generate_dashboard()
