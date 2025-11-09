"""PyTest configuration and fixtures for Selenium login automation.

- Loads environment variables from src/config/.env
- Provides --headless flag
- Creates and tears down WebDriver via driver fixture
- Captures screenshots on test failures and attaches path to pytest-html report when available
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Generator

import pytest
from dotenv import load_dotenv

from src.utils.driver_factory import create_driver
from src.pages.base_page import BasePage


# Load .env from src/config/.env if present
ENV_PATH = Path(__file__).resolve().parents[1] / "config" / ".env"
load_dotenv(dotenv_path=ENV_PATH)


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--headless", action="store_true", default=False, help="Run browser in headless mode")


@pytest.fixture(scope="session")
def headless(request: pytest.FixtureRequest) -> bool:
    return bool(request.config.getoption("--headless"))


@pytest.fixture()
def driver(headless: bool) -> Generator:
    driver = create_driver(headless=headless)
    yield driver
    driver.quit()


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
