"""PyTest configuration and fixtures for Selenium login automation.

- Loads environment variables from src/config/.env
- Provides --headless flag
- Creates and tears down WebDriver via driver fixture
- Captures screenshots on test failures and attaches path to pytest-html report when available
"""

from __future__ import annotations

import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Generator

import pytest
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from src.utils.driver_factory import create_driver
from src.pages.base_page import BasePage

# Load environment variables
env_path = Path(__file__).resolve().parents[2] / "src" / "config" / ".env"
print(f"Loading environment variables from: {env_path}")
if not env_path.exists():
    print("⚠️  .env file not found! Using default values.")

load_dotenv(dotenv_path=env_path)

# Debug: Print important environment variables
print("\n=== Environment Variables ===")
print(f"BASE_URL: {os.getenv('BASE_URL', 'Not set')}")
print(f"VALID_USERNAME: {os.getenv('VALID_USERNAME', 'Not set')}")
print(f"VALID_PASSWORD: {'*' * (len(os.getenv('VALID_PASSWORD', '')) or 0)}")
print("==========================\n")


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--headless", action="store_true", default=False, 
                    help="Run browser in headless mode")
    parser.addoption("--no-quit", action="store_true", default=False,
                    help="Don't quit the browser after tests")


@pytest.fixture(scope="session")
def headless(request: pytest.FixtureRequest) -> bool:
    return bool(request.config.getoption("--headless"))


@pytest.fixture()
def driver(headless: bool, request: pytest.FixtureRequest) -> Generator:
    """Create and yield a WebDriver instance.
    
    By default, keeps the browser open after tests for inspection.
    Use --headless to run in headless mode.
    """
    driver = None
    try:
        print("\n=== Setting up WebDriver ===")
        driver = create_driver(headless=headless)
        driver.maximize_window()
        print(f"Browser: {driver.capabilities['browserName']} {driver.capabilities['browserVersion']}")
        print("==========================\n")
        
        yield driver
        
        # Keep the browser open after test completion
        if not headless:  # Only keep open if not in headless mode
            print("\n💡 Test completed. Browser will remain open for inspection.")
            print("Press Ctrl+C in the terminal to close the browser and exit.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nClosing browser...")
        
    except Exception as e:
        print(f"\n❌ Error during test execution: {str(e)}")
        if driver:
            # Take a screenshot on error
            screenshot_path = Path("screenshots/error.png")
            screenshot_path.parent.mkdir(exist_ok=True)
            driver.save_screenshot(str(screenshot_path))
            print(f"Screenshot saved to: {screenshot_path.absolute()}")
        raise  # Re-raise the exception to fail the test
        
    finally:
        if driver:
            if not request.config.getoption("--no-quit"):
                print("\n=== Tearing down WebDriver ===")
                try:
                    driver.quit()
                    print("Browser closed successfully")
                except Exception as e:
                    print(f"Error closing browser: {e}")
                print("============================\n")
            else:
                print("\nℹ️  Browser kept open due to --no-quit flag")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    # Execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        drv = item.funcargs.get("driver")
        if drv:
            try:
                # Create screenshots directory if it doesn't exist
                screenshots_dir = os.path.join(os.getcwd(), "screenshots")
                os.makedirs(screenshots_dir, exist_ok=True)
                
                # Generate a unique filename
                test_name = item.name.replace("[", "_").replace("]", "_")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{test_name}_{timestamp}.png"
                filepath = os.path.join("screenshots", filename)
                
                # Take screenshot
                try:
                    drv.save_screenshot(filepath)
                    print(f"Screenshot saved to: {os.path.abspath(filepath)}")
                    
                    # Try to attach to pytest-html report if plugin is active
                    try:
                        from pytest_html import extras  # type: ignore
                        extra = getattr(rep, "extra", [])
                        # Attach a link to the saved screenshot
                        extra.append(extras.html(f'<div>Screenshot: <a href="../{filepath}">{filepath}</a></div>'))
                        rep.extra = extra
                    except Exception as e:
                        print(f"Could not attach screenshot to HTML report: {e}")
                        setattr(item, "_screenshot_path", filepath)
                        
                except Exception as e:
                    print(f"Failed to save screenshot: {e}")
                    
            except Exception as e:
                print(f"Error in screenshot handling: {e}")
