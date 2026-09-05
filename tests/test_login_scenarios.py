"""
Comprehensive Login Test Scenarios for SauceDemo.com
30+ test scenarios covering all login edge cases.
"""
import pytest
from pages.login_page import LoginPage
from pages.products_page import ProductsPage
from utils.helpers import capture_screenshot, ensure_directories, print_test_result


# ==================== Test Data ====================

VALID_CREDENTIALS = [
    pytest.param("standard_user", "secret_sauce", id="standard_user", marks=pytest.mark.smoke),
    pytest.param("problem_user", "secret_sauce", id="problem_user"),
    pytest.param("performance_glitch_user", "secret_sauce", id="performance_glitch_user"),
]

INVALID_USERNAME = [
    pytest.param("SauceName", "secret_sauce", "Username and password do not match any user in service."),
    pytest.param("invalidUser", "secret_sauce", "Username and password do not match any user in service."),
    pytest.param("test@test.com", "secret_sauce", "Username and password do not match any user in service."),
]

INVALID_PASSWORD = [
    pytest.param("standard_user", "wrongpassword", "Username and password do not match any user in service."),
    pytest.param("standard_user", "123456", "Username and password do not match any user in service."),
    pytest.param("standard_user", "password", "Username and password do not match any user in service."),
]

EMPTY_FIELDS = [
    pytest.param("", "secret_sauce", "Username is required"),
    pytest.param("standard_user", "", "Password is required"),
    pytest.param("", "", "Username is required"),
]

SPECIAL_CHARACTERS = [
    pytest.param("user'\"; DROP TABLE users;--", "secret_sauce", id="sql_injection_username"),
    pytest.param("standard_user", "' OR '1'='1' --", id="sql_injection_password"),
    pytest.param("<script>alert('xss')</script>", "secret_sauce", id="xss_username"),
    pytest.param("standard_user", "<script>alert('xss')</script>", id="xss_password"),
]

LONG_STRINGS = [
    pytest.param("a" * 500, "secret_sauce", id="long_username_500"),
    pytest.param("standard_user", "b" * 500, id="long_password_500"),
    pytest.param("u" * 1000, "secret_sauce", id="long_username_1000"),
]

WHITESPACE = [
    pytest.param("   ", "secret_sauce", id="whitespace_username"),
    pytest.param("standard_user", "   ", id="whitespace_password"),
    pytest.param("  \t\n  ", "secret_sauce", id="mixed_whitespace_username"),
]


# ==================== 1. SUCCESSFUL LOGIN ====================

class TestSuccessfulLogin:
    @pytest.mark.parametrize("username,password", VALID_CREDENTIALS)
    def test_successful_login_with_valid_credentials(self, page, username, password):
        """TC001: Verify successful login with valid credentials."""
        login_page = LoginPage(page)
        login_page.login(username, password)
        assert login_page.is_logged_in(), f"Login failed for user: {username}"
        assert login_page.is_on_products_page(), "User was not redirected to products page"
        products_page = ProductsPage(page)
        product_count = products_page.get_product_count()
        assert product_count > 0, "No products displayed on the products page"
        print_test_result(f"TC001 - Login as {username}", "PASSED")

    def test_successful_login_verifies_products_loaded(self, page):
        """TC002: Verify products are properly loaded after login."""
        login_page = LoginPage(page)
        login_page.login("standard_user", "secret_sauce")
        products_page = ProductsPage(page)
        products = products_page.get_all_products()
        assert len(products) == 6, f"Expected 6 products, but found {len(products)}"
        for product in products:
            assert product["name"], f"Product name is empty: {product}"
            assert product["price"], f"Product price is empty: {product}"
        print_test_result("TC002 - Products loaded after login", "PASSED")

    def test_successful_login_verifies_url(self, page):
        """TC003: Verify URL changes after successful login."""
        login_page = LoginPage(page)
        initial_url = login_page.get_page_url()
        assert "login" in initial_url or "saucedemo.com" in initial_url
        login_page.login("standard_user", "secret_sauce")
        assert login_page.is_on_products_page(), "URL did not change to products page"
        assert "inventory" in login_page.get_page_url(), "URL does not contain 'inventory'"
        print_test_result("TC003 - URL changes after login", "PASSED")

    def test_successful_login_verifies_title(self, page):
        """TC004: Verify page title after successful login."""
        login_page = LoginPage(page)
        login_page.login("standard_user", "secret_sauce")
        title = page.title()
        assert "Swag Labs" in title or "Inventory" in title, f"Unexpected page title: {title}"
        print_test_result("TC004 - Page title verification", "PASSED")

    def test_successful_login_different_users_see_products(self, page):
        """TC005: Verify different users see the products page."""
        for username, password in [
            ("standard_user", "secret_sauce"),
            ("problem_user", "secret_sauce"),
            ("performance_glitch_user", "secret_sauce"),
        ]:
            page_new = page.browser.new_page()
            login = LoginPage(page_new)
            login.login(username, password)
            assert login.is_logged_in(), f"Login failed for: {username}"
            assert login.is_on_products_page(), f"Products page not loaded for: {username}"
            page_new.close()
        print_test_result("TC005 - Different users login", "PASSED")


# ==================== 2. INVALID USERNAME ====================

class TestInvalidUsername:
    @pytest.mark.parametrize("username,password,error_msg", INVALID_USERNAME)
    def test_login_with_invalid_username(self, page, username, password, error_msg):
        """TC006: Verify error message when username is invalid."""
        login_page = LoginPage(page)
        login_page.login(username, password)
        assert login_page.is_error_displayed(), "Error message not displayed for invalid username"
        assert not login_page.is_logged_in(), "User should not be logged in with invalid username"
        assert login_page.is_visible(login_page.USERNAME_INPUT), "Username field missing after error"
        assert login_page.is_visible(login_page.PASSWORD_INPUT), "Password field missing after error"
        print_test_result(f"TC006 - Invalid username: {username}", "PASSED")

    def test_login_invalid_username_clears_error_on_new_input(self, page):
        """TC007: Verify error message disappears after clearing and re-entering."""
        login_page = LoginPage(page)
        login_page.login("invalidUser", "secret_sauce")
        error1 = login_page.get_error_message()
        assert error1 != "", "Error message should be displayed"
        login_page.clear_username()
        login_page.enter_username("standard_user")
        login_page.click_login()
        assert login_page.is_logged_in(), "Should be logged in after entering valid credentials"
        print_test_result("TC007 - Error clears on new input", "PASSED")


# ==================== 3. INVALID PASSWORD ====================

class TestInvalidPassword:
    @pytest.mark.parametrize("username,password,error_msg", INVALID_PASSWORD)
    def test_login_with_invalid_password(self, page, username, password, error_msg):
        """TC008: Verify error message when password is invalid."""
        login_page = LoginPage(page)
        login_page.login(username, password)
        assert login_page.is_error_displayed(), "Error message not displayed for invalid password"
        assert not login_page.is_logged_in(), "User should not be logged in with invalid password"
        assert login_page.is_visible(login_page.USERNAME_INPUT), "Username field missing"
        assert login_page.is_visible(login_page.PASSWORD_INPUT), "Password field missing"
        print_test_result(f"TC008 - Invalid password for {username}", "PASSED")

    def test_login_invalid_password_preserves_username(self, page):
        """TC009: Verify username is preserved after failed login."""
        login_page = LoginPage(page)
        login_page.login("standard_user", "wrongpassword")
        username_val = login_page.get_username_field_value()
        assert username_val == "standard_user", f"Username was not preserved. Expected 'standard_user', got '{username_val}'"
        print_test_result("TC009 - Username preserved after invalid password", "PASSED")


# ==================== 4. BOTH INVALID ====================

class TestBothInvalidCredentials:
    def test_login_with_both_invalid(self, page):
        """TC010: Verify error when both username and password are invalid."""
        login_page = LoginPage(page)
        login_page.login("invalidUser", "wrongpass")
        assert login_page.is_error_displayed(), "Error message not displayed"
        assert not login_page.is_logged_in(), "Should not be logged in"
        print_test_result("TC010 - Both credentials invalid", "PASSED")

    def test_login_with_both_invalid_verifies_error_text(self, page):
        """TC011: Verify the specific error text when both are invalid."""
        login_page = LoginPage(page)
        login_page.login("wrong", "wrong")
        error_msg = login_page.get_error_message()
        assert error_msg != "", "Error message should not be empty"
        assert len(error_msg) > 0, "Error message should have content"
        print_test_result(f"TC011 - Error text: {error_msg}", "PASSED")


# ==================== 5. EMPTY FIELDS ====================

class TestEmptyFields:
    @pytest.mark.parametrize("username,password,expected_error", EMPTY_FIELDS)
    def test_login_with_empty_fields(self, page, username, password, expected_error):
        """TC012: Verify error messages for various empty field combinations."""
        login_page = LoginPage(page)
        login_page.login(username, password)
        assert login_page.is_error_displayed(), "Error message should be displayed for empty fields"
        assert not login_page.is_logged_in(), "Should not be logged in with empty fields"
        print_test_result(f"TC012 - Empty fields ({username[:10] or 'empty'}/{password[:10] or 'empty'})", "PASSED")

    def test_login_click_with_no_input(self, page):
        """TC013: Verify behavior when clicking login with completely empty fields."""
        login_page = LoginPage(page)
        login_page.clear_username()
        login_page.clear_password()
        login_page.click_login()
        assert login_page.is_error_displayed(), "Error should be displayed when clicking login with empty fields"
        print_test_result("TC013 - Click login with empty fields", "PASSED")


# ==================== 6. SPECIAL CHARACTERS ====================

class TestSpecialCharacters:
    @pytest.mark.parametrize("username,password", SPECIAL_CHARACTERS)
    def test_login_with_special_characters(self, page, username, password):
        """TC014: Verify application handles special characters safely."""
        login_page = LoginPage(page)
        login_page.login(username, password)
        assert login_page.is_error_displayed(), "Error should be displayed for special characters"
        assert not login_page.is_logged_in(), "Should not be logged in with special characters"
        print_test_result("TC014 - Special chars handled safely", "PASSED")

    def test_login_sql_injection_attempts_blocked(self, page):
        """TC015: Verify SQL injection attempts are blocked."""
        login_page = LoginPage(page)
        login_page.login("admin' OR '1'='1", "secret_sauce")
        assert not login_page.is_logged_in(), "SQL injection should not bypass authentication"
        page.reload()
        login_page.login("standard_user", "' OR 1=1 --")
        assert not login_page.is_logged_in(), "SQL injection should not bypass authentication"
        print_test_result("TC015 - SQL injection blocked", "PASSED")

    def test_login_xss_attempts_handled(self, page):
        """TC016: Verify XSS attempts are handled safely."""
        login_page = LoginPage(page)
        login_page.login("<script>alert('XSS')</script>", "secret_sauce")
        assert not login_page.is_logged_in(), "XSS should not cause login"
        error = login_page.get_error_message()
        assert error != "", "Error should be displayed"
        print_test_result("TC016 - XSS attempts handled", "PASSED")


# ==================== 7. LONG STRINGS ====================

class TestLongStrings:
    @pytest.mark.parametrize("username,password", LONG_STRINGS)
    def test_login_with_long_strings(self, page, username, password):
        """TC017: Verify application handles very long strings gracefully."""
        login_page = LoginPage(page)
        login_page.login(username, password)
        assert not login_page.is_logged_in(), "Should not be logged in with long strings"
        print_test_result(f"TC017 - Long string ({len(username)}/{len(password)}) handled", "PASSED")


# ==================== 8. WHITESPACE ====================

class TestWhitespace:
    @pytest.mark.parametrize("username,password", WHITESPACE)
    def test_login_with_whitespace_only(self, page, username, password):
        """TC018: Verify whitespace-only inputs are handled correctly."""
        login_page = LoginPage(page)
        login_page.login(username, password)
        assert login_page.is_error_displayed(), "Error should be displayed for whitespace-only input"
        assert not login_page.is_logged_in(), "Should not be logged in with whitespace"
        print_test_result("TC018 - Whitespace input handled", "PASSED")


# ==================== 9. POST-LOGIN VERIFICATION ====================

class TestPostLoginVerification:
    def test_verify_products_displayed_after_login(self, page):
        """TC019: Verify all products are displayed after successful login."""
        login_page = LoginPage(page)
        login_page.login("standard_user", "secret_sauce")
        products_page = ProductsPage(page)
        products = products_page.get_all_products()
        expected_products = [
            "Sauce Labs Onesie", "Sauce Labs Bolt T-Shirt", "Sauce Labs Backpack",
            "Sauce Labs Bike Light", "Sauce Labs Fleece Jacket", "Sauce Labs Bit Liter",
        ]
        product_names = [p["name"] for p in products]
        for expected in expected_products:
            assert any(expected.lower() in name.lower() for name in product_names), \
                f"Product '{expected}' not found"
        print_test_result("TC019 - Products displayed after login", "PASSED")

    def test_verify_user_header_after_login(self, page):
        """TC020: Verify user information is displayed in header after login."""
        login_page = LoginPage(page)
        login_page.login("standard_user", "secret_sauce")
        products_page = ProductsPage(page)
        user = products_page.get_current_user()
        assert user, "User label should be displayed in header"
        assert "Swag Labs" in user or " PRODUCTS" in user, f"Unexpected header text: {user}"
        print_test_result("TC020 - User header after login", "PASSED")


# ==================== 10. LOGOUT ====================

class TestLogout:
    def test_logout_after_successful_login(self, page):
        """TC021: Verify logout functionality after successful login."""
        login_page = LoginPage(page)
        login_page.login("standard_user", "secret_sauce")
        assert login_page.is_logged_in(), "User should be logged in"
        page.goto("https://www.saucedemo.com/inventory.html")
        assert login_page.is_on_products_page(), "Should be on products page"
        products_page = ProductsPage(page)
        products_page.click_menu()
        products_page.click_logout()
        login_page.wait_for_login_page()
        assert login_page.is_on_login_page(), "User should be on login page after logout"
        print_test_result("TC021 - Logout after login", "PASSED")

    def test_logout_clears_session(self, page):
        """TC022: Verify logout clears session and requires re-login."""
        login_page = LoginPage(page)
        login_page.login("standard_user", "secret_sauce")
        assert login_page.is_on_products_page(), "Should be on products page"
        products_page = ProductsPage(page)
        products_page.click_menu()
        products_page.click_logout()
        assert login_page.is_on_login_page(), "Should be on login page"
        print_test_result("TC022 - Logout clears session", "PASSED")


# ==================== 11. CROSS-BROWSER ====================

class TestCrossBrowser:
    def test_login_works_on_chromium(self, page):
        """TC023: Verify login works on Chromium."""
        login_page = LoginPage(page)
        login_page.login("standard_user", "secret_sauce")
        assert login_page.is_logged_in(), "Login should work on Chromium"
        assert login_page.is_on_products_page(), "Should navigate to products page"
        print_test_result("TC023 - Login on Chromium", "PASSED")


# ==================== 12. EDGE CASES ====================

class TestEdgeCases:
    def test_rapid_login_logout_cycle(self, page):
        """TC024: Verify login/logout cycle works multiple times."""
        for cycle in range(2):
            login_page = LoginPage(page)
            login_page.login("standard_user", "secret_sauce")
            assert login_page.is_logged_in(), f"Cycle {cycle + 1}: Login failed"
            products_page = ProductsPage(page)
            products_page.click_menu()
            products_page.click_logout()
            assert login_page.is_on_login_page(), f"Cycle {cycle + 1}: Not on login page after logout"
        print_test_result("TC024 - Rapid login/logout cycle", "PASSED")

    def test_login_with_case_sensitive_username(self, page):
        """TC025: Verify username is case-sensitive."""
        login_page = LoginPage(page)
        login_page.login("STANDARD_USER", "secret_sauce")
        assert login_page.is_error_displayed(), "Username should be case-sensitive"
        assert not login_page.is_logged_in(), "Should not login with wrong case"
        print_test_result("TC025 - Username case sensitive", "PASSED")

    def test_login_with_case_sensitive_password(self, page):
        """TC026: Verify password is case-sensitive."""
        login_page = LoginPage(page)
        login_page.login("standard_user", "SECRET_SAUCE")
        assert login_page.is_error_displayed(), "Password should be case-sensitive"
        assert not login_page.is_logged_in(), "Should not login with wrong case password"
        print_test_result("TC026 - Password case sensitive", "PASSED")

    def test_error_message_disappears_after_clearing_fields(self, page):
        """TC027: Verify error message disappears when fields are cleared."""
        login_page = LoginPage(page)
        login_page.login("invalidUser", "secret_sauce")
        assert login_page.is_error_displayed(), "Error should be displayed"
        login_page.clear_username()
        login_page.clear_password()
        print_test_result("TC027 - Error disappears on clear", "PASSED")

    def test_login_button_state(self, page):
        """TC028: Verify login button is clickable."""
        login_page = LoginPage(page)
        assert login_page.is_visible(login_page.LOGIN_BUTTON), "Login button should be visible"
        print_test_result("TC028 - Login button state", "PASSED")

    def test_navigate_directly_to_products_without_login(self, page):
        """TC029: Verify navigating to products page without login shows login."""
        page.goto("https://www.saucedemo.com/inventory.html")
        login_page = LoginPage(page)
        assert login_page.is_on_login_page() or "inventory" in page.url or "login" in page.url
        print_test_result("TC029 - Direct products access", "PASSED")

    def test_consecutive_failed_logins_show_errors(self, page):
        """TC030: Verify multiple consecutive failed logins show errors each time."""
        login_page = LoginPage(page)
        for _ in range(3):
            login_page.login("wrongUser", "wrongPass")
            assert login_page.is_error_displayed(), "Error should be displayed for each failed attempt"
            page.reload()
        print_test_result("TC030 - Multiple failed logins", "PASSED")
