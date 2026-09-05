"""
Pytest configuration for Playwright test automation framework.
"""
import pytest
from playwright.sync_api import sync_playwright, Browser, BrowserContext

BASE_URL = "https://www.saucedemo.com"
SCREENSHOTS_DIR = "reports/screenshots"
REPORTS_DIR = "reports"

VALID_USERS = {
    "standard": {"username": "standard_user", "password": "secret_sauce"},
    "problem_user": {"username": "problem_user", "password": "secret_sauce"},
    "performance_glitch_user": {"username": "performance_glitch_user", "password": "secret_sauce"},
}

INVALID_CREDENTIALS = {
    "invalid_username": {"username": "SauceName", "password": "secret_sauce"},
    "invalid_password": {"username": "standard_user", "password": "wrongpassword"},
    "both_invalid": {"username": "SauceName", "password": "wrongpassword"},
    "empty_username": {"username": "", "password": "secret_sauce"},
    "empty_password": {"username": "standard_user", "password": ""},
    "both_empty": {"username": "", "password": ""},
}


@pytest.fixture(scope="session")
def browser_context():
    """Create a browser context for the session."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            base_url=BASE_URL,
        )
        yield context
        context.close()
        browser.close()


@pytest.fixture(scope="function")
def page(browser_context):
    """Create a fresh page for each test."""
    new_page = browser_context.new_page()
    yield new_page
    new_page.close()


@pytest.fixture(scope="function")
def login_page(page):
    """Provide a LoginPage instance."""
    from pages.login_page import LoginPage
    return LoginPage(page)


@pytest.fixture(scope="function")
def products_page(page):
    """Provide a ProductsPage instance."""
    from pages.products_page import ProductsPage
    return ProductsPage(page)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture screenshot on test failure."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        try:
            pg = item.funcargs.get("page")
            if pg:
                from utils.helpers import capture_screenshot
                screenshot_path = capture_screenshot(pg, item.nodeid)
                report.sections.append(("Screenshot", f"See reports/screenshots/{screenshot_path}"))
        except Exception as e:
            report.sections.append(("Screenshot Error", str(e)))
