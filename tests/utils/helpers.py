"""
Utility functions for the test automation framework.
"""
import os
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
SCREENSHOTS_DIR = BASE_DIR.parent / "reports" / "screenshots"
REPORTS_DIR = BASE_DIR.parent / "reports"


def ensure_directories():
    """Ensure all required directories exist."""
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def generate_screenshot_filename(test_name: str) -> str:
    """Generate a unique filename for screenshots."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    safe_name = test_name.replace("tests/", "").replace("/", "_").replace(" ", "_")
    return f"{safe_name}_{timestamp}.png"


def capture_screenshot(page, test_name: str, path: str = None) -> str:
    """Capture a screenshot of the current page and save it."""
    ensure_directories()
    if path is None:
        filename = generate_screenshot_filename(test_name)
        path = str(SCREENSHOTS_DIR / filename)
    else:
        ensure_directories()
        filename = os.path.basename(path)
    page.screenshot(path=path, full_page=True)
    return filename


def get_current_timestamp() -> str:
    """Get the current timestamp as a string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def print_test_result(test_name: str, status: str, duration: float = 0, error: str = None):
    """Print a formatted test result."""
    status_icon = "✅" if status == "PASSED" else "❌"
    message = f"[{status_icon}] {test_name} - {status}"
    if duration > 0:
        message += f" ({duration:.2f}s)"
    if error:
        message += f"\n   Error: {error}"
    print(message)
