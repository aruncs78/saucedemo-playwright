"""
Login Page Object Model for SauceDemo.com
Handles all interactions with the login page.
"""
from pages.base_page import BasePage


class LoginPage(BasePage):
    """Page Object for the SauceDemo login page."""

    # Locators
    USERNAME_INPUT = "#user-name"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "#login-button"
    ERROR_CONTAINER = ".error-button"
    ERROR_MESSAGE = ".error-message-container"
    PAGE_TITLE = "Swag Labs"

    # URL
    LOGIN_URL = "https://www.saucedemo.com"

    def __init__(self, page):
        super().__init__(page)
        self.navigate(self.LOGIN_URL)
        self.wait_for_login_page()

    def wait_for_login_page(self, timeout: int = 15000):
        """Wait for the login page to be fully loaded."""
        self.page.wait_for_selector(self.USERNAME_INPUT, timeout=timeout)
        self.page.wait_for_selector(self.PASSWORD_INPUT, timeout=timeout)
        self.page.wait_for_selector(self.LOGIN_BUTTON, timeout=timeout)

    def enter_username(self, username: str):
        """Enter username into the username field."""
        self.page.locator(self.USERNAME_INPUT).fill(username)

    def enter_password(self, password: str):
        """Enter password into the password field."""
        self.page.locator(self.PASSWORD_INPUT).fill(password)

    def click_login(self):
        """Click the login button."""
        self.page.locator(self.LOGIN_BUTTON).click()

    def login(self, username: str, password: str):
        """Complete login flow: enter credentials and click login."""
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()

    def get_error_message(self, timeout: int = 5000) -> str:
        """Get the error message text if displayed."""
        try:
            error_elem = self.page.locator(self.ERROR_CONTAINER)
            if error_elem.is_visible(timeout=timeout):
                return error_elem.inner_text(timeout=timeout)
        except Exception:
            pass
        try:
            error_elem = self.page.locator(self.ERROR_MESSAGE)
            if error_elem.is_visible(timeout=timeout):
                return error_elem.inner_text(timeout=timeout)
        except Exception:
            pass
        return ""

    def is_error_displayed(self, timeout: int = 3000) -> bool:
        """Check if an error message is displayed."""
        return (
            self.is_visible(self.ERROR_CONTAINER, timeout) or
            self.is_visible(self.ERROR_MESSAGE, timeout)
        )

    def is_logged_in(self, timeout: int = 5000) -> bool:
        """Check if the user is successfully logged in."""
        return (
            not self.is_visible(self.USERNAME_INPUT, timeout=2000) and
            not self.is_visible(self.PASSWORD_INPUT, timeout=2000)
        )

    def get_username_field_value(self) -> str:
        """Get the current value of the username field."""
        return self.page.locator(self.USERNAME_INPUT).input_value()

    def get_password_field_value(self) -> str:
        """Get the current value of the password field."""
        return self.page.locator(self.PASSWORD_INPUT).input_value()

    def clear_username(self):
        """Clear the username field."""
        self.page.locator(self.USERNAME_INPUT).fill("")

    def clear_password(self):
        """Clear the password field."""
        self.page.locator(self.PASSWORD_INPUT).fill("")

    def get_page_url(self) -> str:
        """Get the current page URL."""
        return self.page.url

    def is_on_products_page(self) -> bool:
        """Check if we've navigated to the products page."""
        return "inventory" in self.page.url

    def is_on_login_page(self) -> bool:
        """Check if we're still on the login page."""
        return "login" in self.page.url or "saucedemo.com" in self.page.url
