"""
Base Page class providing common methods for all page objects.
Follows the Page Object Model (POM) pattern.
"""
from playwright.sync_api import Page, Locator


class BasePage:
    """Base page class with common interaction methods."""

    def __init__(self, page: Page):
        self.page = page

    def navigate(self, url: str):
        """Navigate to the specified URL."""
        self.page.goto(url, wait_until="domcontentloaded", timeout=30000)

    def get_url(self) -> str:
        """Get the current page URL."""
        return self.page.url

    def get_title(self) -> str:
        """Get the current page title."""
        return self.page.title()

    def click(self, selector: str, timeout: int = 10000):
        """Click an element by selector."""
        self.page.locator(selector).click(timeout=timeout)

    def fill(self, selector: str, value: str, timeout: int = 10000):
        """Fill an input field with the given value."""
        self.page.locator(selector).fill(value, timeout=timeout)

    def get_text(self, selector: str, timeout: int = 10000) -> str:
        """Get text content of an element."""
        return self.page.locator(selector).inner_text(timeout=timeout)

    def is_visible(self, selector: str, timeout: int = 5000) -> bool:
        """Check if an element is visible."""
        try:
            return self.page.locator(selector).is_visible(timeout=timeout)
        except Exception:
            return False

    def is_enabled(self, selector: str, timeout: int = 5000) -> bool:
        """Check if an element is enabled."""
        try:
            return self.page.locator(selector).is_enabled(timeout=timeout)
        except Exception:
            return False

    def get_attribute(self, selector: str, attribute: str) -> str:
        """Get an attribute of an element."""
        return self.page.locator(selector).get_attribute(attribute)

    def take_screenshot(self, path: str = None):
        """Take a screenshot of the current page."""
        if path:
            self.page.screenshot(path=path, full_page=True)
        else:
            return self.page.screenshot(full_page=True)

    def wait_for_load_state(self, state: str = "networkidle", timeout: int = 30000):
        """Wait for a specific page load state."""
        self.page.wait_for_load_state(state, timeout=timeout)

    def wait_for_url(self, url_pattern: str, timeout: int = 10000):
        """Wait for the URL to match a pattern."""
        self.page.wait_for_url(url_pattern, timeout=timeout)

    def expect_to_have_url(self, expected_url: str, timeout: int = 10000):
        """Assert the page has the expected URL."""
        current = self.page.url
        assert current == expected_url, f"Expected URL '{expected_url}', but got '{current}'"

    def expect_to_have_title(self, expected_title: str, timeout: int = 10000):
        """Assert the page has the expected title."""
        actual = self.page.title()
        assert expected_title.lower() in actual.lower(), \
            f"Expected title to contain '{expected_title}', but got '{actual}'"

    def clear_and_fill(self, selector: str, value: str):
        """Clear a field and fill with new value."""
        self.page.locator(selector).click()
        self.page.locator(selector).fill("")
        self.page.locator(selector).fill(value)

    def press_key(self, selector: str, key: str):
        """Press a key on an element."""
        self.page.locator(selector).press(key)
