"""Core module for Windows UI automation."""
from typing import Dict, Any, Optional, List, Union
from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import sys

class WindowsAutomation:
    def __init__(self, app_path: str):
        """Initialize the automation with application path."""
        self.app_path = app_path
        self.driver = None
        self.debug = True  # Enable detailed logging
    
    def _get_capabilities(self) -> dict:
        """Get the capabilities for WinAppDriver."""
        caps = {
            "platformName": "Windows",
            "deviceName": "WindowsPC",
            "app": self.app_path,
            "ms:waitForAppLaunch": "1"
        }
        return caps
    
    def connect(self, wait_time: int = 1) -> None:
        """Connect to the application."""
        caps = self._get_capabilities()
        print(f"\nConnecting with capabilities: {caps}")
        
        try:
            self.driver = webdriver.Remote(
                command_executor='http://127.0.0.1:4723',
                desired_capabilities=caps
            )
            print("Successfully connected!")
        except Exception as e:
            print(f"Failed to connect: {e}")
            raise
    
    def disconnect(self) -> None:
        """Disconnect from the application."""
        if self.driver:
            try:
                self.driver.quit()
                print("Successfully disconnected.")
            except Exception as e:
                print(f"Error during disconnect: {e}")

    def send_keys(self, keys) -> None:
        """Send keyboard keys to the application."""
        if self.driver:
            actions = ActionChains(self.driver)
            actions.send_keys(keys)
            actions.perform()
        
    def get_active_element_text(self) -> str:
        """Get the text of the currently focused/active element."""
        try:
            # Try multiple approaches to get the text
            element = self.driver.switch_to.active_element
            
            # Get text using different attributes
            name_attr = element.get_attribute("Name")
            auto_id = element.get_attribute("AutomationId")
            class_name = element.get_attribute("ClassName")
            text = element.text
            
            if self.debug:
                print("\nElement properties:")
                print(f"  Text: '{text}'")
                print(f"  Name: '{name_attr}'")
                print(f"  AutomationId: '{auto_id}'")
                print(f"  ClassName: '{class_name}'")
            
            # Try to get parent menu item text if this is a submenu
            try:
                parent = element.find_element_by_xpath('..')
                parent_text = parent.get_attribute("Name")
                if parent_text:
                    print(f"  Parent menu: '{parent_text}'")
            except:
                pass
            
            # Return the first non-empty value in order of preference
            for value in [name_attr, text, auto_id]:
                if value and value.strip() and value.strip() != parent_text:
                    return value.strip()
            
            return ""
        except Exception as e:
            if self.debug:
                print(f"Error getting element text: {e}")
            return ""

    def get_all_menu_items(self) -> List[str]:
        """Try to get all visible menu items."""
        try:
            # Try to find menu items using different strategies
            items = []
            
            # Try by name
            elements = self.driver.find_elements_by_class_name("MenuItem")
            if elements:
                items.extend([e.get_attribute("Name") for e in elements])
            
            # Try by accessibility ID
            elements = self.driver.find_elements_by_accessibility_id("MenuItems")
            if elements:
                items.extend([e.get_attribute("Name") for e in elements])
            
            if self.debug:
                print("\nAll visible menu items:")
                for item in items:
                    print(f"  - '{item}'")
            
            return [item for item in items if item and item.strip()]
        except Exception as e:
            if self.debug:
                print(f"Error getting menu items: {e}")
            return []

    def navigate_menu(self, menu_path: List[str], submenu_delay: float = 0.2) -> None:
        """Navigate through menu items using element discovery approach."""
        if not self.driver or not menu_path:
            return
            
        print(f"\nNavigating to: {' -> '.join(menu_path)}")
        
        try:
            # Store initial UI state
            initial_elements = set()
            elements = self.driver.find_elements_by_xpath("//*")
            for elem in elements:
                try:
                    name = elem.get_attribute("Name")
                    if name:
                        initial_elements.add(name)
                except:
                    continue
            
            if self.debug:
                print("\nInitial UI elements:", initial_elements)
            
            # Click the top-level menu
            self.click_menu_item(menu_path[0])
            time.sleep(submenu_delay)
            
            # Look for submenu item
            if len(menu_path) > 1:
                target_item = menu_path[1]
                print(f"\nLooking for submenu item: '{target_item}'")
                
                # Find new elements that appeared
                elements = self.driver.find_elements_by_xpath("//*")
                for elem in elements:
                    try:
                        name = elem.get_attribute("Name")
                        if name and name not in initial_elements:
                            if self.debug:
                                print(f"Found new menu item: '{name}'")
                            if target_item.lower() in name.lower():
                                print(f"Found matching menu item: '{name}'")
                                elem.click()
                                return
                    except Exception as e:
                        if self.debug:
                            print(f"Error processing element: {e}")
                        continue
                
                print(f"Could not find submenu item: '{target_item}'")
                self.send_keys(Keys.ESCAPE)  # Close menu if not found
                
        except Exception as e:
            print(f"Menu navigation failed: {e}")
            try:
                self.send_keys(Keys.ESCAPE)  # Try to close menu on error
            except:
                pass  # Ignore errors during cleanup

    def click_menu_item(self, menu_text: str) -> None:
        """Click a menu item by its text."""
        try:
            # Find and click the menu item
            menu_item = self.driver.find_element_by_name(menu_text)
            print(f"Clicking menu item: '{menu_text}'")
            menu_item.click()
            print(f"Successfully clicked: '{menu_text}'")
        except Exception as e:
            print(f"Failed to click menu item '{menu_text}': {e}")
            raise  # Re-raise to let caller handle it

    def click_button(self, button_text: str) -> bool:
        """Click a button by its text (optimized for standard buttons)."""
        try:
            button = self.driver.find_element_by_name(button_text)
            if self.debug:
                print(f"Clicking button: '{button_text}'")
            button.click()
            return True
        except Exception as e:
            if self.debug:
                print(f"Failed to click button '{button_text}': {e}")
            return False

    def select_treeview_item(self, item_text: str) -> bool:
        """Select an item in a treeview by its text."""
        try:
            item = self.driver.find_element_by_name(item_text)
            if self.debug:
                print(f"Selecting treeview item: '{item_text}'")
            item.click()
            return True
        except Exception as e:
            if self.debug:
                print(f"Failed to select treeview item '{item_text}': {e}")
            return False

    def fill_form_field(self, field_name: str, value: str) -> bool:
        """Fill a form field by its label/name."""
        try:
            field = self.driver.find_element_by_name(field_name)
            if self.debug:
                print(f"Filling field '{field_name}' with value '{value}'")
            field.clear()
            field.send_keys(value)
            return True
        except Exception as e:
            if self.debug:
                print(f"Failed to fill field '{field_name}': {e}")
            return False

    def wait_for_element(self, element_name: str, timeout: int = 5) -> bool:
        """Wait for an element to become available."""
        try:
            self.driver.implicitly_wait(timeout)
            element = self.driver.find_element_by_name(element_name)
            return element.is_displayed()
        except:
            return False
        finally:
            self.driver.implicitly_wait(0)  # Reset wait

    def _cleanup_keyboard_state(self) -> None:
        """Thoroughly clean up keyboard state, including all modifiers and toggles."""
        if not self.driver:
            return
            
        try:
            cleanup = ActionChains(self.driver)
            
            # Release all possible modifier keys
            cleanup.key_up(Keys.CONTROL)
            cleanup.key_up(Keys.ALT)
            cleanup.key_up(Keys.SHIFT)
            cleanup.key_up(Keys.META)  # Windows key
            cleanup.key_up(Keys.COMMAND)  # For completeness
            
            # Handle Caps Lock - press it if it's on to turn it off
            # Note: This assumes Caps Lock is not needed for the automation
            cleanup.key_down(Keys.NULL)  # Reset keyboard state
            cleanup.key_up(Keys.NULL)
            
            # Send Escape to close any open menus
            cleanup.send_keys(Keys.ESCAPE)
            
            cleanup.perform()
            time.sleep(0.1)  # Small delay to ensure cleanup is complete
        except Exception as e:
            if self.debug:
                print(f"Keyboard cleanup warning: {e}")

    def navigate_by_shortcut(self, shortcut_sequence: List[str], delay_between: float = 0.15) -> None:
        """Navigate using keyboard shortcuts.
        
        Args:
            shortcut_sequence: List of shortcuts (e.g. ['alt+f', 'n'] for File->New)
            delay_between: Delay between shortcuts in seconds
        """
        if not self.driver:
            return
            
        try:
            for shortcut in shortcut_sequence:
                if self.debug:
                    print(f"Sending shortcut: {shortcut}")
                
                # Split into modifier and key if it's a combination
                parts = shortcut.lower().split('+')
                
                actions = ActionChains(self.driver)
                
                # If it's a combination (e.g., alt+f)
                if len(parts) > 1:
                    # Hold modifier
                    if 'alt' in parts:
                        actions.key_down(Keys.ALT)
                    if 'ctrl' in parts:
                        actions.key_down(Keys.CONTROL)
                    if 'shift' in parts:
                        actions.key_down(Keys.SHIFT)
                    
                    # Press the actual key
                    actions.send_keys(parts[-1])
                    
                    # Release modifiers
                    if 'alt' in parts:
                        actions.key_up(Keys.ALT)
                    if 'ctrl' in parts:
                        actions.key_up(Keys.CONTROL)
                    if 'shift' in parts:
                        actions.key_up(Keys.SHIFT)
                else:
                    # Just a single key
                    actions.send_keys(parts[0])
                
                actions.perform()
                time.sleep(delay_between)
                
            if self.debug:
                print("Shortcut sequence completed")
                
        except Exception as e:
            print(f"Failed to send shortcut: {e}")
            
    def __enter__(self):
        """Support for 'with' statement."""
        self.connect(1)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support for 'with' statement."""
        self.disconnect() 