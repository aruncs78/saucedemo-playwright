"""
Products Page Object Model for SauceDemo.com
Handles interactions after successful login.
"""
from pages.base_page import BasePage


class ProductsPage(BasePage):
    """Page Object for the SauceDemo products/inventory page."""

    # Locators
    HEADER = ".app_header"
    USERNAME_LABEL = ".app_header .title"
    PRODUCTS_GRID = ".inventory_list"
    PRODUCT_ITEM = ".inventory_item"
    PRODUCT_NAME = ".inventory_item_name"
    PRODUCT_PRICE = ".inventory_item_price"
    ADD_TO_CART_BUTTONS = ".btn.btn_primary.btn_small.btn_inventory"
    REMOVE_FROM_CART_BUTTON = ".btn.btn_secondary.btn_small.btn_inventory"
    CART_BADGE = ".shopping_cart_badge"
    LOGOUT_BUTTON = "#logout_sidebar_link"
    MENU_BUTTON = "#background_menu_container > header > div > div.menu_wrap > span"

    PRODUCTS_URL_PATTERN = "*inventory*"

    def __init__(self, page):
        super().__init__(page)

    def get_current_user(self) -> str:
        """Get the currently logged-in user name from header."""
        return self.page.locator(self.USERNAME_LABEL).inner_text()

    def get_all_products(self) -> list:
        """Get all product names and prices."""
        products = []
        product_elements = self.page.locator(self.PRODUCT_ITEM).all()
        for elem in product_elements:
            name = elem.locator(self.PRODUCT_NAME).inner_text()
            price = elem.locator(self.PRODUCT_PRICE).inner_text()
            products.append({"name": name, "price": price})
        return products

    def get_product_count(self) -> int:
        """Get the total number of products displayed."""
        return self.page.locator(self.PRODUCT_ITEM).count()

    def add_to_cart(self, product_name: str):
        """Add a specific product to cart by name."""
        product_index = self._find_product_index(product_name)
        if product_index is not None:
            buttons = self.page.locator(self.ADD_TO_CART_BUTTONS).all()
            buttons[product_index].click()

    def remove_from_cart(self, product_name: str):
        """Remove a product from cart."""
        product_index = self._find_product_index(product_name)
        if product_index is not None:
            buttons = self.page.locator(self.REMOVE_FROM_CART_BUTTON).all()
            if product_index < len(buttons):
                buttons[product_index].click()

    def _find_product_index(self, product_name: str) -> int:
        """Find the index of a product by name."""
        products = self.page.locator(self.PRODUCT_ITEM).all()
        for i, product in enumerate(products):
            name = product.locator(self.PRODUCT_NAME).inner_text()
            if product_name.lower() in name.lower():
                return i
        return -1

    def get_cart_count(self) -> int:
        """Get the number of items in the cart from the badge."""
        try:
            badge = self.page.locator(self.CART_BADGE)
            text = badge.inner_text()
            return int(text) if text.isdigit() else 0
        except Exception:
            return 0

    def click_logout(self):
        """Click the logout button."""
        self.page.locator(self.LOGOUT_BUTTON).click()

    def click_menu(self):
        """Click the menu/hamburger button to reveal logout option."""
        self.page.locator(self.MENU_BUTTON).click()

    def is_logged_in(self) -> bool:
        """Verify user is logged in by checking page URL."""
        return "inventory" in self.page.url

    def is_product_displayed(self, product_name: str) -> bool:
        """Check if a specific product is displayed on the page."""
        products = self.get_all_products()
        return any(product_name.lower() in p["name"].lower() for p in products)
