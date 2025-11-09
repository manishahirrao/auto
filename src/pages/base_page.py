"""Base page object providing common WebDriver interactions and waits."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Tuple

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


Locator = Tuple[str, str]


class BasePage:
    """Base class for all Page Objects."""

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver

    def find(self, by_locator: Locator) -> WebElement:
        return WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(by_locator))

    def click(self, by_locator: Locator) -> None:
        elem = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(by_locator))
        elem.click()

    def send_keys(self, by_locator: Locator, text: str) -> None:
        elem = self.find(by_locator)
        elem.clear()
        elem.send_keys(text)

    def get_text(self, by_locator: Locator) -> str:
        elem = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(by_locator))
        return elem.text

    def is_visible(self, by_locator: Locator, timeout: int = 5) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(by_locator))
            return True
        except Exception:
            return False

    def take_screenshot(self, filename: str | None = None) -> str:
        """Save a PNG screenshot under screenshots/ and return file path.

        Filename will be normalized and appended with timestamp if not provided.
        """
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not filename:
            filename = f"screenshot_{ts}.png"
        else:
            # Ensure it ends with .png
            if not filename.lower().endswith(".png"):
                filename = f"{filename}_{ts}.png"
        os.makedirs("screenshots", exist_ok=True)
        path = os.path.join("screenshots", filename)
        self.driver.save_screenshot(path)
        return path
