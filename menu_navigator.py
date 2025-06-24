"""Helper utilities for navigating traditional Windows menu bars."""
import time
from typing import Sequence

from appium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException

MENU_CLICK_TIMEOUT_SEC = 5  # Maximum time to wait for each menu item
MENU_APPEAR_DELAY_SEC = 0.3  # Time to wait for submenu to appear


def click_menu_path(driver: webdriver.Remote, menu_path: Sequence[str]) -> None:
    """Click each menu item in sequence.

    Args:
        driver: Active WinAppDriver session
        menu_path: Ordered list of menu captions to click

    Raises:
        ValueError: If menu_path is empty
        TimeoutException: If menu item not found within timeout
        RuntimeError: If any menu item cannot be found
    """
    if not menu_path:
        raise ValueError("menu_path cannot be empty")

    for caption in menu_path:
        start_time = time.time()
        while True:
            try:
                element = driver.find_element_by_name(caption)
                element.click()
                time.sleep(MENU_APPEAR_DELAY_SEC)  # brief pause for submenu to appear
                break  # Success - move to next menu item
            except NoSuchElementException:
                if time.time() - start_time > MENU_CLICK_TIMEOUT_SEC:
                    raise TimeoutException(f"Menu item not found within {MENU_CLICK_TIMEOUT_SEC}s: {caption}")
                time.sleep(0.1)  # Small delay before retry
            except Exception as exc:
                raise RuntimeError(f"Error clicking menu item: {caption}") from exc 