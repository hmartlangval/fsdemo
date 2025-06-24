"""Core module for Windows UI automation."""
from typing import Dict, Any, Optional, List, Union
from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import sys
import win32gui
import win32con
from window_discovery import find_window_handle_by_title

class WindowsAutomation:
    def __init__(self, app_identifier: str, use_title: bool = False):
        """Initialize the automation with either application path or window title.
        
        Args:
            app_identifier: Either the path to the .exe file or the window title to find
            use_title: If True, app_identifier is treated as a window title to find.
                      If False, app_identifier is treated as an .exe path.
        """
        self.app_identifier = app_identifier
        self.use_title = use_title
        self.window_info = None
        self.driver = None
        self.desktop_driver = None  # Desktop session for window discovery
        self.debug = True  # Enable detailed logging
        
        # If using title, try to find the window immediately
        if self.use_title:
            self.window_info = find_window_handle_by_title(self.app_identifier)
            if not self.window_info:
                raise ValueError(f"Could not find window with title containing: {self.app_identifier}")
            if self.debug:
                print(f"Found window: {self.window_info}")
    
    def _verify_window_state(self, hwnd: int, max_retries: int = 5, retry_delay: float = 0.5) -> bool:
        """Verify that the window is in a proper state for automation.
        
        Args:
            hwnd: Window handle to verify
            max_retries: Maximum number of verification attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            bool: True if window is in proper state, False otherwise
        """
        for attempt in range(max_retries):
            try:
                # Check if window still exists
                if not win32gui.IsWindow(hwnd):
                    if self.debug:
                        print(f"Window {hwnd} no longer exists")
                    return False
                
                # Check if window is visible
                if not win32gui.IsWindowVisible(hwnd):
                    if self.debug:
                        print(f"Window {hwnd} is not visible")
                    continue
                
                # Check if window is foreground
                if win32gui.GetForegroundWindow() != hwnd:
                    if self.debug:
                        print(f"Window {hwnd} is not foreground, attempt {attempt + 1}")
                    # Try to bring to foreground again
                    win32gui.SetForegroundWindow(hwnd)
                    time.sleep(retry_delay)
                    continue
                
                # Get window placement to verify not minimized
                placement = win32gui.GetWindowPlacement(hwnd)
                if placement[1] == win32con.SW_SHOWMINIMIZED:
                    if self.debug:
                        print(f"Window {hwnd} is minimized")
                    continue
                
                # All checks passed
                return True
                
            except Exception as e:
                if self.debug:
                    print(f"Error verifying window state: {e}")
                time.sleep(retry_delay)
                continue
            
        return False
    
    def _bring_window_to_foreground(self) -> bool:
        """Bring the window to the foreground for automation.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.window_info:
            return False
            
        hwnd = self.window_info['hwnd']
        try:
            # Show window if it's minimized
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.5)  # Wait for restore animation
            
            # Try multiple times to bring window to foreground
            for _ in range(3):  # Try up to 3 times
                # Enable the window
                win32gui.EnableWindow(hwnd, True)
                # Set focus and activate
                win32gui.SetForegroundWindow(hwnd)
                # Force window to be restored and active
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                win32gui.UpdateWindow(hwnd)
                
                # Longer delay to let window manager stabilize
                time.sleep(1.0)
                
                # Verify window state
                if self._verify_window_state(hwnd):
                    if self.debug:
                        print("Successfully brought window to foreground and verified state")
                    # Additional delay after successful verification
                    time.sleep(0.5)
                    return True
            
            if self.debug:
                print("Warning: Could not bring window to foreground")
            return False
            
        except Exception as e:
            if self.debug:
                print(f"Error bringing window to foreground: {e}")
            return False
    
    def _get_capabilities_for_app_path(self) -> dict:
        """Get capabilities for launching new application."""
        return {
            "platformName": "Windows",
            "deviceName": "WindowsPC",
            "app": self.app_identifier,
            "ms:waitForAppLaunch": "1"
        }
    
    def _get_capabilities_for_desktop(self) -> dict:
        """Get capabilities for desktop session."""
        return {
            "platformName": "Windows",
            "deviceName": "WindowsPC",
            "app": "Root"
        }
    
    def _get_capabilities_for_window_handle(self) -> dict:
        """Get capabilities for existing window using handle."""
        hwnd_hex = hex(self.window_info['hwnd'])
        return {
            "platformName": "Windows",
            "deviceName": "WindowsPC",
            "appTopLevelWindow": hwnd_hex
        }
    
    def _connect_via_desktop_session(self) -> bool:
        """Try to connect via desktop session and find the window.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.debug:
                print("Attempting desktop session approach...")
            
            # Create desktop session
            desktop_caps = self._get_capabilities_for_desktop()
            self.desktop_driver = webdriver.Remote(
                command_executor='http://127.0.0.1:4723',
                desired_capabilities=desktop_caps
            )
            
            if self.debug:
                print("Desktop session created successfully")
            
            # Try to find the window by name
            window_name = self.window_info['title']
            try:
                window_element = self.desktop_driver.find_element_by_name(window_name)
                if self.debug:
                    print(f"Found window element: {window_name}")
                
                # Get the NativeWindowHandle
                native_handle = window_element.get_attribute("NativeWindowHandle")
                if native_handle and native_handle != "0":
                    if self.debug:
                        print(f"Got NativeWindowHandle: {native_handle}")
                    
                    # Convert to hex format
                    handle_int = int(native_handle)
                    handle_hex = hex(handle_int)
                    
                    # Close desktop session
                    self.desktop_driver.quit()
                    self.desktop_driver = None
                    
                    # Try to connect with the native window handle
                    caps = {
                        "platformName": "Windows",
                        "deviceName": "WindowsPC",
                        "appTopLevelWindow": handle_hex
                    }
                    
                    self.driver = webdriver.Remote(
                        command_executor='http://127.0.0.1:4723',
                        desired_capabilities=caps
                    )
                    
                    if self.debug:
                        print("Successfully connected via desktop session approach")
                    return True
                    
            except Exception as e:
                if self.debug:
                    print(f"Could not find window in desktop session: {e}")
            
            # Clean up desktop session if we get here
            if self.desktop_driver:
                self.desktop_driver.quit()
                self.desktop_driver = None
                
        except Exception as e:
            if self.debug:
                print(f"Desktop session approach failed: {e}")
            if self.desktop_driver:
                try:
                    self.desktop_driver.quit()
                except:
                    pass
                self.desktop_driver = None
        
        return False
    
    def _connect_via_direct_handle(self) -> bool:
        """Try to connect directly using window handle.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.debug:
                print("Attempting direct handle approach...")
            
            # Try different handle formats
            hwnd = self.window_info['hwnd']
            handle_formats = [
                str(hwnd),           # Decimal string
                hex(hwnd),           # Hex string
                f"0x{hwnd:X}",       # Hex with 0x prefix
                f"{hwnd:08X}",       # 8-digit hex
            ]
            
            for handle_format in handle_formats:
                try:
                    caps = {
                        "platformName": "Windows",
                        "deviceName": "WindowsPC",
                        "appTopLevelWindow": handle_format
                    }
                    
                    if self.debug:
                        print(f"Trying handle format: {handle_format}")
                    
                    self.driver = webdriver.Remote(
                        command_executor='http://127.0.0.1:4723',
                        desired_capabilities=caps
                    )
                    
                    if self.debug:
                        print(f"Successfully connected with handle format: {handle_format}")
                    return True
                    
                except Exception as e:
                    if self.debug:
                        print(f"Handle format {handle_format} failed: {e}")
                    continue
            
        except Exception as e:
            if self.debug:
                print(f"Direct handle approach failed: {e}")
        
        return False
    
    def connect(self, wait_time: int = 1) -> None:
        """Connect to the application using multiple fallback approaches."""
        
        # For app path, use the original approach
        if not self.use_title:
            caps = self._get_capabilities_for_app_path()
            print(f"\nConnecting with app path capabilities: {caps}")
            
            try:
                self.driver = webdriver.Remote(
                    command_executor='http://127.0.0.1:4723',
                    desired_capabilities=caps
                )
                print("Successfully connected!")
                return
            except Exception as e:
                print(f"Failed to connect: {e}")
                raise
        
        # For title-based automation, try multiple approaches
        if not self._bring_window_to_foreground():
            print("Warning: Could not bring window to foreground, continuing anyway...")
        
        # Try multiple connection approaches in order of preference
        connection_methods = [
            ("Desktop Session", self._connect_via_desktop_session),
            ("Direct Handle", self._connect_via_direct_handle),
        ]
        
        for method_name, method_func in connection_methods:
            try:
                if self.debug:
                    print(f"\nTrying {method_name} approach...")
                
                if method_func():
                    print(f"Successfully connected using {method_name} approach!")
                    return
                    
            except Exception as e:
                if self.debug:
                    print(f"{method_name} approach failed: {e}")
                continue
        
        # If all approaches fail, raise an error
        raise RuntimeError(
            f"Failed to connect to window '{self.app_identifier}' using all available methods. "
            f"Window info: {self.window_info}"
        )
    
    def disconnect(self) -> None:
        """Disconnect from the application."""
        if self.driver:
            try:
                self.driver.quit()
                print("Successfully disconnected from main session.")
            except Exception as e:
                print(f"Error during main session disconnect: {e}")
        
        if self.desktop_driver:
            try:
                self.desktop_driver.quit()
                print("Successfully disconnected from desktop session.")
            except Exception as e:
                print(f"Error during desktop session disconnect: {e}")

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