"""WebDriver factory to create and configure Selenium Chrome driver.

- Uses ChromeDriver available on PATH.
- Supports headless via --headless=new flag.
- Sets implicit wait to 5 seconds and window size to 1920x1080.
"""

from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service


def create_driver(headless: bool = True) -> webdriver.Chrome:
    """Create and return a configured Chrome WebDriver instance.

    Args:
        headless: Whether to run browser in headless mode.

    Returns:
        Configured Chrome WebDriver.
    """
    options = ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    if headless:
        # Use new headless for Chrome 109+
        options.add_argument("--headless=new")

    service = Service()  # Uses chromedriver from PATH
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(5)
    return driver
