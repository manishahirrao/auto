"""End-to-end tests for GitHub login and logout flows using the LoginPage POM.

These tests use environment variables from src/config/.env for configuration.
"""

from __future__ import annotations

import os
import time
from typing import Generator

import pytest
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.pages.login_page import LoginPage

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../src/config/.env"))

# Get configuration from environment variables
BASE_URL = os.getenv("BASE_URL", "https://www.saucedemo.com/")
VALID_USERNAME = os.getenv("VALID_USERNAME", "standard_user")
VALID_PASSWORD = os.getenv("VALID_PASSWORD", "secret_sauce")
LOCKED_USER = os.getenv("LOCKED_USER", "locked_out_user")

# Sauce Demo specific locators
INVENTORY_CONTAINER = (By.ID, "inventory_container")
MENU_BUTTON = (By.ID, "react-burger-menu-btn")
LOGOUT_BUTTON = (By.ID, "logout_sidebar_link")


def is_logged_in(driver: WebDriver) -> bool:
    """Check if user is logged in by looking for the inventory container."""
    try:
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "inventory_container"))
        )
        return True
    except:
        return False


def ensure_logged_out(driver: WebDriver, page: LoginPage) -> None:
    """Ensure the user is logged out before test."""
    try:
        # Try to load the Sauce Demo home page
        driver.get("https://www.saucedemo.com/")
        
        # If logged in, log out
        if is_logged_in(driver):
            # Click the menu button
            menu_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "react-burger-menu-btn"))
            )
            menu_button.click()
            
            # Click the logout button
            logout_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "logout_sidebar_link"))
            )
            logout_button.click()
            
            # Wait for the logout to complete
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "login_button_container"))
            )
    except Exception as e:
        print(f"Warning during logout: {str(e)}")
        # If anything fails, just go to the login page
        driver.get(BASE_URL)


@pytest.fixture(autouse=True)
def setup_teardown(driver: WebDriver, request: pytest.FixtureRequest) -> Generator:
    """Ensure we're logged out before each test and clean up after."""
    page = LoginPage(driver)
    ensure_logged_out(driver, page)
    
    # This will run after each test
    def teardown() -> None:
        try:
            # Take a screenshot if the test failed
            if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                test_name = request.node.name
                # Ensure screenshots directory exists
                os.makedirs("screenshots", exist_ok=True)
                screenshot_path = f"screenshots/{test_name}_{timestamp}.png"
                driver.save_screenshot(screenshot_path)
                print(f"Screenshot saved to {screenshot_path}")
        except Exception as e:
            print(f"Error during teardown: {str(e)}")
    
    request.addfinalizer(teardown)


@pytest.mark.skipif(not (VALID_USERNAME and VALID_PASSWORD), 
                  reason="VALID_USERNAME and VALID_PASSWORD must be set in .env")
def test_valid_login_logout(driver: WebDriver) -> None:
    """Test successful login and logout flow."""
    page = LoginPage(driver)
    page.load(BASE_URL)

    # Log in with valid credentials
    page.login(VALID_USERNAME, VALID_PASSWORD)
    
    # Verify login success by checking for inventory container
    assert page.is_visible(page.INVENTORY_CONTAINER), "Inventory container not visible after login"
    
    # Log out
    page.logout()
    
    # Verify logout by checking if login button is visible again
    assert page.is_visible(page.LOGIN_BTN), "Login button not visible after logout"


def test_invalid_login(driver: WebDriver) -> None:
    """Test login with invalid credentials shows an error message."""
    page = LoginPage(driver)
    page.load(BASE_URL)

    # Attempt to log in with invalid credentials
    try:
        page.login("invalid_user", "wrong_password")
        assert False, "Login should have failed with invalid credentials"
    except Exception as e:
        # Check if the error message is as expected
        error_text = str(e).lower()
        assert "login failed" in error_text or "epic sadface" in error_text, \
            f"Unexpected error message: {error_text}"


def test_blank_fields(driver: WebDriver) -> None:
    """Test that login fails with blank username and password."""
    page = LoginPage(driver)
    page.load(BASE_URL)
    
    # Click login without entering any credentials
    page.click(page.LOGIN_BTN)
    
    # Verify error message is displayed
    error_elements = driver.find_elements(*page.ERROR_MSG)
    assert error_elements, "No error message displayed for blank credentials"
    error_text = error_elements[0].text.strip()
    assert "required" in error_text.lower() or "empty" in error_text.lower() or "epic sadface" in error_text.lower(), \
        f"Unexpected error message: {error_text}"


def test_locked_out_user(driver: WebDriver) -> None:
    """Test login with a locked out user shows appropriate error."""
    page = LoginPage(driver)
    page.load(BASE_URL)
    
    # Attempt to log in with locked out user
    try:
        page.login(LOCKED_USER, VALID_PASSWORD)
        assert False, "Login should have failed for locked out user"
    except Exception as e:
        # Check if the error message is as expected
        error_text = str(e)
        assert "locked out" in error_text.lower() or "epic sadface" in error_text.lower(), \
            f"Unexpected error message: {error_text}"
