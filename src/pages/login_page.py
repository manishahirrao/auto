"""Login page object implementing login and logout flows.

Locators are placeholders; update them to match your target application.
"""

from __future__ import annotations

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.support.ui import WebDriverWait

from .base_page import BasePage, Locator


class LoginPage(BasePage):
    """Page Object for the application's Login page."""

    # Sauce Demo login page locators
    USERNAME: Locator = (By.ID, "user-name")  # Username field
    PASSWORD: Locator = (By.ID, "password")   # Password field
    LOGIN_BTN: Locator = (By.ID, "login-button")  # Login button

    # Sauce Demo elements
    ERROR_MSG: Locator = (By.CSS_SELECTOR, "h3[data-test='error']")  # Error message container
    INVENTORY_CONTAINER: Locator = (By.ID, "inventory_container")  # Visible after successful login
    MENU_BUTTON: Locator = (By.ID, "react-burger-menu-btn")  # Menu button for logout
    LOGOUT_BUTTON: Locator = (By.ID, "logout_sidebar_link")  # Logout link in menu

    def load(self, url: str) -> None:
        self.driver.get(url)

    def login(self, username: str, password: str) -> None:
        try:
            # Wait for the page to load completely
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Wait for username field with explicit wait
            username_field = WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located(self.USERNAME)
            )
            
            # Clear and enter username
            username_field.clear()
            username_field.send_keys(username)
            
            # Enter password
            password_field = self.driver.find_element(*self.PASSWORD)
            password_field.clear()
            password_field.send_keys(password)
            
            # Click login button
            login_button = self.driver.find_element(*self.LOGIN_BTN)
            login_button.click()
            
            # Wait for either login success or error
            try:
                # First check for error message (appears quickly if login fails)
                error_element = WebDriverWait(self.driver, 3).until(
                    EC.visibility_of_element_located(self.ERROR_MSG)
                )
                # If we get here, there was an error
                error_text = error_element.text.strip()
                raise Exception(f"Login failed: {error_text}")
                
            except TimeoutException:
                # If no error, wait for successful login page
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.visibility_of_element_located(self.INVENTORY_CONTAINER)
                    )
                except TimeoutException:
                    # Check if there's an error message that we might have missed
                    error_elements = self.driver.find_elements(*self.ERROR_MSG)
                    if error_elements and error_elements[0].is_displayed():
                        error_text = error_elements[0].text.strip()
                        if error_text:
                            raise Exception(f"Login failed: {error_text}")
                    raise Exception("Login timed out - neither success nor error page loaded")
            
        except Exception as e:
            # Take a screenshot for any exception
            self.take_screenshot(f"login_error_{username}")
            raise

    def get_error(self) -> str:
        return self.get_text(self.ERROR_MSG)

    def logout(self, max_retries: int = 3) -> None:
        """Log out from the application with retry mechanism.
        
        Args:
            max_retries: Maximum number of retry attempts
            
        Raises:
            Exception: If logout fails after all retry attempts
        """
        for attempt in range(max_retries):
            try:
                # Wait for the menu button with a fresh find
                menu_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(self.MENU_BUTTON)
                )
                
                # Scroll into view and click with JavaScript
                self.driver.execute_script("arguments[0].scrollIntoView(true);", menu_button)
                self.driver.execute_script("arguments[0].click();", menu_button)
                
                # Wait for the logout button with a fresh find
                WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located(self.LOGOUT_BUTTON)
                )
                
                # Find and click logout button with JavaScript
                logout_button = self.driver.find_element(*self.LOGOUT_BUTTON)
                self.driver.execute_script("arguments[0].click();", logout_button)
        
                # Wait for the login page to load
                WebDriverWait(self.driver, 10).until(
                    lambda d: d.find_element(*self.USERNAME).is_displayed()
                )
                
                # If we got here, logout was successful
                return
                
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    self.take_screenshot("logout_error")
                    raise Exception(f"Logout failed after {max_retries} attempts: {str(e)}")
                
                # Wait a bit before retrying
                time.sleep(1)
                print(f"Retry {attempt + 1}/{max_retries} - Retrying logout...")
