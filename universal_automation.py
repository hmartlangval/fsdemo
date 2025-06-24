"""Universal Windows Application Automation System.

This module provides a centralized automation framework that can handle different
types of Windows applications (Java, .NET, Win32, etc.) through auto-detection
and specialized handlers.
"""

import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from windows_automation import WindowsAutomation


class BaseWindowAutomation:
    """Base class for all window automation implementations."""
    
    def __init__(self, app_identifier, use_title=True):
        """Initialize base automation.
        
        Args:
            app_identifier: Application path or window title
            use_title: Whether app_identifier is a window title
        """
        self.app_identifier = app_identifier
        self.use_title = use_title
        self.automation = None
        self.app_type = None
        self.window_info = None
        
    def connect(self):
        """Connect to the application using desktop session approach."""
        try:
            print(f"=== CONNECTING TO APPLICATION ===")
            print(f"Target: '{self.app_identifier}'")
            
            # Create automation instance
            self.automation = WindowsAutomation(self.app_identifier, use_title=self.use_title)
            self.automation.connect()
            
            # Detect application type
            self.app_type = self.detect_application_type()
            print(f"✅ Connected! Application type: {self.app_type}")
            
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def detect_application_type(self):
        """Detect the type of application we're connected to.
        
        Returns:
            str: 'java', 'dotnet', 'win32', 'uwp', 'unknown'
        """
        try:
            # Get main window element
            window_element = self.automation.driver.find_element_by_xpath("//Window")
            
            # Get window class name and other properties
            class_name = window_element.get_attribute("ClassName") or ""
            framework_id = window_element.get_attribute("FrameworkId") or ""
            process_name = window_element.get_attribute("ProcessId") or ""
            
            print(f"Window analysis:")
            print(f"  ClassName: '{class_name}'")
            print(f"  FrameworkId: '{framework_id}'")
            print(f"  ProcessId: '{process_name}'")
            
            # Store window info for later use
            self.window_info = {
                'class_name': class_name,
                'framework_id': framework_id,
                'process_id': process_name
            }
            
            # Detection logic
            if 'SunAwt' in class_name or 'Java' in class_name:
                return 'java'
            elif framework_id == 'WPF' or 'Wpf' in class_name:
                return 'dotnet_wpf'
            elif framework_id == 'WinForm' or 'WindowsForms' in class_name:
                return 'dotnet_winforms'
            elif framework_id == 'XAML' or class_name.startswith('Windows.UI'):
                return 'uwp'
            elif class_name.startswith('#32770') or 'Dialog' in class_name:
                return 'win32_dialog'
            elif framework_id == 'Win32' or any(keyword in class_name.lower() for keyword in ['notepad', 'calculator', 'edit', 'button', 'static']):
                return 'win32'
            else:
                return 'unknown'
                
        except Exception as e:
            print(f"⚠️ Error detecting app type: {e}")
            return 'unknown'
    
    def disconnect(self):
        """Disconnect from the application."""
        try:
            if self.automation:
                self.automation.disconnect()
                print("✅ Disconnected successfully")
        except Exception as e:
            print(f"⚠️ Error during disconnect: {e}")
    
    def cleanup_dialogs(self):
        """Clean up any open dialogs or menus."""
        try:
            if self.automation and self.automation.driver:
                actions = ActionChains(self.automation.driver)
                # Send escape keys to close dialogs/menus
                for _ in range(3):
                    actions.send_keys(Keys.ESCAPE).perform()
                    time.sleep(0.2)
        except Exception as e:
            print(f"⚠️ Error during cleanup: {e}")
    
    def get_all_elements(self):
        """Get all UI elements in the current window."""
        try:
            return self.automation.driver.find_elements_by_xpath("//*")
        except Exception as e:
            print(f"⚠️ Error getting elements: {e}")
            return []
    
    # Default implementations (can be overridden by subclasses)
    def navigate_menu(self, menu_path, target_item):
        """Navigate to a menu item. Default implementation for detection purposes.
        
        Args:
            menu_path: Menu path (e.g., "File", "Edit", etc.)
            target_item: Target menu item to select
            
        Returns:
            bool: Success/failure
        """
        print(f"⚠️ Base class navigate_menu called - no implementation")
        return False
    
    def identify_dialog_elements(self, wait_timeout=5):
        """Identify elements in a dialog that appeared. Default implementation.
        
        Args:
            wait_timeout: Maximum time to wait for dialog
            
        Returns:
            dict: Dialog information with elements
        """
        print(f"⚠️ Base class identify_dialog_elements called - no implementation")
        return {'type': 'none', 'elements': [], 'input_fields': [], 'buttons': []}
    
    def fill_form_inputs(self, input_data):
        """Fill form inputs with provided data. Default implementation.
        
        Args:
            input_data: Dictionary of input field data
            
        Returns:
            bool: Success/failure
        """
        print(f"⚠️ Base class fill_form_inputs called - no implementation")
        return False


class JavaWindowAutomation(BaseWindowAutomation):
    """Specialized automation for Java Swing applications."""
    
    def navigate_menu(self, menu_path, target_item):
        """Navigate Java Swing menu using keyboard shortcuts.
        
        Args:
            menu_path: Menu name (e.g., "File", "Edit", "Actions")
            target_item: Menu item to find (e.g., "New", "Open", "Save")
            
        Returns:
            bool: Success/failure
        """
        try:
            print(f"\n=== JAVA MENU NAVIGATION ===")
            print(f"Menu: {menu_path} → {target_item}")
            
            # Map menu names to keyboard shortcuts
            menu_shortcuts = {
                'file': 'f',
                'edit': 'e', 
                'view': 'v',
                'actions': 'a',
                'configuration': 'c',
                'config': 'c',
                'help': 'h',
                'tools': 't',
                'window': 'w'
            }
            
            # Get shortcut for menu
            menu_key = menu_shortcuts.get(menu_path.lower())
            if not menu_key:
                print(f"❌ Unknown menu: {menu_path}")
                return False
            
            # Open menu with Alt+Key
            actions = ActionChains(self.automation.driver)
            print(f"Opening menu with Alt+{menu_key.upper()}")
            actions.key_down(Keys.ALT).send_keys(menu_key).key_up(Keys.ALT).perform()
            time.sleep(1)
            
            # Navigate through menu items
            print(f"Searching for: '{target_item}'")
            max_attempts = 15
            
            for attempt in range(max_attempts):
                try:
                    # Get current focused element text
                    current_text = self.automation.get_active_element_text()
                    print(f"  [{attempt + 1}] Current: '{current_text}'")
                    
                    # Check if we found our target
                    if target_item.lower() in current_text.lower():
                        print(f"  ✅ Found: '{current_text}'")
                        # Press Enter to select
                        actions.send_keys(Keys.ENTER).perform()
                        time.sleep(1)
                        return True
                    
                    # Move to next item
                    actions.send_keys(Keys.ARROW_DOWN).perform()
                    time.sleep(0.3)
                    
                except Exception as e:
                    print(f"  ⚠️ Navigation error: {e}")
                    continue
            
            print(f"❌ Item '{target_item}' not found after {max_attempts} attempts")
            actions.send_keys(Keys.ESCAPE).perform()  # Close menu
            return False
            
        except Exception as e:
            print(f"❌ Java menu navigation failed: {e}")
            return False
    
    def identify_dialog_elements(self, wait_timeout=5):
        """Identify elements in Java dialog."""
        try:
            print(f"\n=== JAVA DIALOG IDENTIFICATION ===")
            
            # Get baseline element count
            initial_elements = self.get_all_elements()
            initial_count = len(initial_elements)
            print(f"Initial elements: {initial_count}")
            
            # Wait for dialog to appear
            dialog_detected = False
            for wait_attempt in range(wait_timeout * 2):
                current_elements = self.get_all_elements()
                current_count = len(current_elements)
                
                if current_count > initial_count + 3:
                    dialog_detected = True
                    print(f"✅ Dialog detected: {initial_count} → {current_count} elements")
                    break
                    
                time.sleep(0.5)
            
            if not dialog_detected:
                return {'type': 'none', 'elements': [], 'input_fields': [], 'buttons': []}
            
            # Wait for dialog to fully load
            time.sleep(1)
            
            # Analyze dialog elements
            return self._analyze_dialog_elements()
            
        except Exception as e:
            print(f"❌ Java dialog identification failed: {e}")
            return {'type': 'error', 'elements': [], 'input_fields': [], 'buttons': []}
    
    def _analyze_dialog_elements(self):
        """Analyze Java dialog elements."""
        try:
            all_elements = self.get_all_elements()
            
            # Find input fields using multiple strategies
            input_fields = []
            input_strategies = [
                ("Edit controls", "//Edit"),
                ("Text inputs", "//Text[@IsKeyboardFocusable='true']"),
                ("ComboBox controls", "//ComboBox"),
            ]
            
            for strategy_name, xpath in input_strategies:
                try:
                    found_inputs = self.automation.driver.find_elements_by_xpath(xpath)
                    for input_elem in found_inputs:
                        try:
                            if input_elem.get_attribute("IsKeyboardFocusable") == "true":
                                input_fields.append({
                                    'element': input_elem,
                                    'name': input_elem.get_attribute("Name") or "",
                                    'type': input_elem.get_attribute("ControlType"),
                                    'strategy': strategy_name
                                })
                        except:
                            continue
                except:
                    continue
            
            # Find buttons
            buttons = []
            try:
                button_elements = self.automation.driver.find_elements_by_xpath("//Button")
                for btn in button_elements:
                    try:
                        buttons.append({
                            'element': btn,
                            'name': btn.get_attribute("Name") or "",
                            'enabled': btn.get_attribute("IsEnabled") == "true"
                        })
                    except:
                        continue
            except:
                pass
            
            # Classify dialog type
            dialog_info = {
                'elements': all_elements,
                'input_fields': input_fields,
                'buttons': buttons
            }
            
            if len(input_fields) >= 2:
                dialog_info['type'] = 'multi_input_form'
            elif len(input_fields) == 1:
                dialog_info['type'] = 'single_input_form'
            elif len(buttons) > 0:
                dialog_info['type'] = 'button_dialog'
            else:
                dialog_info['type'] = 'unknown'
            
            print(f"✅ Java dialog analyzed: {dialog_info['type']} ({len(input_fields)} inputs, {len(buttons)} buttons)")
            return dialog_info
            
        except Exception as e:
            print(f"❌ Java dialog analysis failed: {e}")
            return {'type': 'error', 'elements': [], 'input_fields': [], 'buttons': []}
    
    def fill_form_inputs(self, input_data):
        """Fill Java form inputs.
        
        Args:
            input_data: List of strings or dict with field names/values
        """
        try:
            print(f"\n=== JAVA FORM FILLING ===")
            
            # Get current dialog info
            dialog_info = self.identify_dialog_elements(wait_timeout=2)
            input_fields = dialog_info.get('input_fields', [])
            
            if not input_fields:
                print("❌ No input fields found")
                return False
            
            # Handle different input data formats
            if isinstance(input_data, list):
                # Fill by position
                for i, value in enumerate(input_data):
                    if i < len(input_fields):
                        field = input_fields[i]
                        print(f"📝 Filling field {i+1}: '{value}'")
                        try:
                            field['element'].click()
                            time.sleep(0.2)
                            field['element'].clear()
                            field['element'].send_keys(str(value))
                            time.sleep(0.3)
                        except Exception as e:
                            print(f"  ❌ Error filling field {i+1}: {e}")
                            return False
            
            elif isinstance(input_data, dict):
                # Fill by field name matching
                for field_name, value in input_data.items():
                    matching_field = None
                    for field in input_fields:
                        if field_name.lower() in field['name'].lower():
                            matching_field = field
                            break
                    
                    if matching_field:
                        print(f"📝 Filling '{field_name}': '{value}'")
                        try:
                            matching_field['element'].click()
                            time.sleep(0.2)
                            matching_field['element'].clear()
                            matching_field['element'].send_keys(str(value))
                            time.sleep(0.3)
                        except Exception as e:
                            print(f"  ❌ Error filling '{field_name}': {e}")
                            return False
                    else:
                        print(f"  ⚠️ Field '{field_name}' not found")
            
            print("✅ Java form filled successfully")
            return True
            
        except Exception as e:
            print(f"❌ Java form filling failed: {e}")
            return False


class DotNetWindowAutomation(BaseWindowAutomation):
    """Specialized automation for .NET applications (WPF/WinForms)."""
    
    def navigate_menu(self, menu_path, target_item):
        """Navigate .NET menu using UI Automation."""
        try:
            print(f"\n=== .NET MENU NAVIGATION ===")
            print(f"Menu: {menu_path} → {target_item}")
            
            # Try to find menu bar
            try:
                menu_bar = self.automation.driver.find_element_by_xpath("//MenuBar")
                print("✅ Found MenuBar")
            except:
                print("⚠️ MenuBar not found, trying Menu elements")
                menu_bar = None
            
            # Find the main menu
            menu_xpath = f"//Menu[@Name='{menu_path}' or contains(@Name, '{menu_path}')]"
            try:
                main_menu = self.automation.driver.find_element_by_xpath(menu_xpath)
                print(f"✅ Found menu: {menu_path}")
                
                # Click to open menu
                main_menu.click()
                time.sleep(0.5)
                
                # Find the target menu item
                item_xpath = f"//MenuItem[@Name='{target_item}' or contains(@Name, '{target_item}')]"
                menu_item = self.automation.driver.find_element_by_xpath(item_xpath)
                print(f"✅ Found menu item: {target_item}")
                
                # Click the menu item
                menu_item.click()
                time.sleep(0.5)
                
                return True
                
            except Exception as e:
                print(f"❌ .NET menu navigation failed: {e}")
                return False
                
        except Exception as e:
            print(f"❌ .NET menu navigation error: {e}")
            return False
    
    def identify_dialog_elements(self, wait_timeout=5):
        """Identify elements in .NET dialog."""
        try:
            print(f"\n=== .NET DIALOG IDENTIFICATION ===")
            
            # Wait for dialog window to appear
            dialog_found = False
            for attempt in range(wait_timeout * 2):
                try:
                    # Look for dialog windows
                    dialogs = self.automation.driver.find_elements_by_xpath("//Window[@ClassName='#32770' or contains(@Name, 'Dialog')]")
                    if dialogs:
                        dialog_found = True
                        print(f"✅ Found {len(dialogs)} dialog(s)")
                        break
                except:
                    pass
                time.sleep(0.5)
            
            if not dialog_found:
                return {'type': 'none', 'elements': [], 'input_fields': [], 'buttons': []}
            
            # Analyze dialog elements
            return self._analyze_dotnet_dialog()
            
        except Exception as e:
            print(f"❌ .NET dialog identification failed: {e}")
            return {'type': 'error', 'elements': [], 'input_fields': [], 'buttons': []}
    
    def _analyze_dotnet_dialog(self):
        """Analyze .NET dialog elements."""
        try:
            # Find input controls
            input_fields = []
            input_xpaths = [
                "//Edit",
                "//TextBox", 
                "//ComboBox",
                "//Text[@IsKeyboardFocusable='true']"
            ]
            
            for xpath in input_xpaths:
                try:
                    elements = self.automation.driver.find_elements_by_xpath(xpath)
                    for elem in elements:
                        try:
                            if elem.get_attribute("IsKeyboardFocusable") == "true":
                                input_fields.append({
                                    'element': elem,
                                    'name': elem.get_attribute("Name") or "",
                                    'type': elem.get_attribute("ControlType")
                                })
                        except:
                            continue
                except:
                    continue
            
            # Find buttons
            buttons = []
            try:
                button_elements = self.automation.driver.find_elements_by_xpath("//Button")
                for btn in button_elements:
                    try:
                        buttons.append({
                            'element': btn,
                            'name': btn.get_attribute("Name") or "",
                            'enabled': btn.get_attribute("IsEnabled") == "true"
                        })
                    except:
                        continue
            except:
                pass
            
            # Classify dialog
            dialog_info = {
                'input_fields': input_fields,
                'buttons': buttons
            }
            
            if len(input_fields) >= 2:
                dialog_info['type'] = 'multi_input_form'
            elif len(input_fields) == 1:
                dialog_info['type'] = 'single_input_form'
            else:
                dialog_info['type'] = 'button_dialog'
            
            print(f"✅ .NET dialog analyzed: {dialog_info['type']} ({len(input_fields)} inputs, {len(buttons)} buttons)")
            return dialog_info
            
        except Exception as e:
            print(f"❌ .NET dialog analysis failed: {e}")
            return {'type': 'error', 'input_fields': [], 'buttons': []}
    
    def fill_form_inputs(self, input_data):
        """Fill .NET form inputs."""
        try:
            print(f"\n=== .NET FORM FILLING ===")
            
            # Get dialog info
            dialog_info = self.identify_dialog_elements(wait_timeout=2)
            input_fields = dialog_info.get('input_fields', [])
            
            if not input_fields:
                print("❌ No input fields found")
                return False
            
            # Fill inputs (similar to Java but with .NET specific handling)
            if isinstance(input_data, list):
                for i, value in enumerate(input_data):
                    if i < len(input_fields):
                        field = input_fields[i]
                        print(f"📝 Filling .NET field {i+1}: '{value}'")
                        try:
                            field['element'].click()
                            time.sleep(0.1)
                            field['element'].clear()
                            field['element'].send_keys(str(value))
                            time.sleep(0.2)
                        except Exception as e:
                            print(f"  ❌ Error: {e}")
                            return False
            
            print("✅ .NET form filled successfully")
            return True
            
        except Exception as e:
            print(f"❌ .NET form filling failed: {e}")
            return False


class Win32WindowAutomation(BaseWindowAutomation):
    """Basic automation for Win32 applications (Notepad, Calculator, etc.)."""
    
    def navigate_menu(self, menu_path, target_item):
        """Navigate Win32 menu using UI Automation."""
        try:
            print(f"\n=== WIN32 MENU NAVIGATION ===")
            print(f"Menu: {menu_path} → {target_item}")
            
            # Try to find menu bar or menu items directly
            try:
                # Look for MenuBar first
                menu_bar = self.automation.driver.find_element_by_xpath("//MenuBar")
                print("✅ Found MenuBar")
                
                # Find the main menu
                menu_xpath = f"//Menu[@Name='{menu_path}' or contains(@Name, '{menu_path}')]"
                main_menu = self.automation.driver.find_element_by_xpath(menu_xpath)
                main_menu.click()
                time.sleep(0.5)
                
                # Find the target menu item
                item_xpath = f"//MenuItem[@Name='{target_item}' or contains(@Name, '{target_item}')]"
                menu_item = self.automation.driver.find_element_by_xpath(item_xpath)
                menu_item.click()
                time.sleep(0.5)
                
                print("✅ Win32 menu navigation successful")
                return True
                
            except Exception as e:
                print(f"⚠️ UI Automation menu failed, trying keyboard shortcuts: {e}")
                
                # Fallback to keyboard shortcuts (like Alt+F)
                actions = ActionChains(self.automation.driver)
                menu_key = menu_path[0].lower()  # First letter of menu name
                actions.key_down(Keys.ALT).send_keys(menu_key).key_up(Keys.ALT).perform()
                time.sleep(1)
                
                # Try to find the menu item by typing first letter
                item_key = target_item[0].lower()
                actions.send_keys(item_key).perform()
                time.sleep(0.5)
                
                print("✅ Win32 keyboard navigation attempted")
                return True
                
        except Exception as e:
            print(f"❌ Win32 menu navigation failed: {e}")
            return False
    
    def identify_dialog_elements(self, wait_timeout=5):
        """Identify elements in Win32 dialog."""
        try:
            print(f"\n=== WIN32 DIALOG IDENTIFICATION ===")
            
            # Wait for new window or dialog
            time.sleep(1)
            
            # Get all elements
            all_elements = self.get_all_elements()
            
            # Find input fields
            input_fields = []
            input_xpaths = [
                "//Edit",
                "//ComboBox", 
                "//Text[@IsKeyboardFocusable='true']"
            ]
            
            for xpath in input_xpaths:
                try:
                    elements = self.automation.driver.find_elements_by_xpath(xpath)
                    for elem in elements:
                        try:
                            if elem.get_attribute("IsKeyboardFocusable") == "true":
                                input_fields.append({
                                    'element': elem,
                                    'name': elem.get_attribute("Name") or "",
                                    'type': elem.get_attribute("ControlType")
                                })
                        except:
                            continue
                except:
                    continue
            
            # Find buttons
            buttons = []
            try:
                button_elements = self.automation.driver.find_elements_by_xpath("//Button")
                for btn in button_elements:
                    try:
                        buttons.append({
                            'element': btn,
                            'name': btn.get_attribute("Name") or "",
                            'enabled': btn.get_attribute("IsEnabled") == "true"
                        })
                    except:
                        continue
            except:
                pass
            
            # Classify dialog
            dialog_info = {
                'elements': all_elements,
                'input_fields': input_fields,
                'buttons': buttons
            }
            
            if len(input_fields) >= 2:
                dialog_info['type'] = 'multi_input_form'
            elif len(input_fields) == 1:
                dialog_info['type'] = 'single_input_form'
            elif len(buttons) > 0:
                dialog_info['type'] = 'button_dialog'
            else:
                dialog_info['type'] = 'none'
            
            print(f"✅ Win32 dialog analyzed: {dialog_info['type']} ({len(input_fields)} inputs, {len(buttons)} buttons)")
            return dialog_info
            
        except Exception as e:
            print(f"❌ Win32 dialog identification failed: {e}")
            return {'type': 'error', 'elements': [], 'input_fields': [], 'buttons': []}
    
    def fill_form_inputs(self, input_data):
        """Fill Win32 form inputs."""
        try:
            print(f"\n=== WIN32 FORM FILLING ===")
            
            # Get dialog info
            dialog_info = self.identify_dialog_elements(wait_timeout=2)
            input_fields = dialog_info.get('input_fields', [])
            
            if not input_fields:
                print("❌ No input fields found")
                return False
            
            # Fill inputs
            if isinstance(input_data, list):
                for i, value in enumerate(input_data):
                    if i < len(input_fields):
                        field = input_fields[i]
                        print(f"📝 Filling Win32 field {i+1}: '{value}'")
                        try:
                            field['element'].click()
                            time.sleep(0.1)
                            field['element'].clear()
                            field['element'].send_keys(str(value))
                            time.sleep(0.2)
                        except Exception as e:
                            print(f"  ❌ Error: {e}")
                            return False
            
            print("✅ Win32 form filled successfully")
            return True
            
        except Exception as e:
            print(f"❌ Win32 form filling failed: {e}")
            return False


class UniversalWindowAutomation:
    """Universal automation system that auto-detects and delegates to specialized handlers."""
    
    def __init__(self, app_identifier, use_title=True):
        """Initialize universal automation system.
        
        Args:
            app_identifier: Application path or window title
            use_title: Whether app_identifier is a window title
        """
        self.app_identifier = app_identifier
        self.use_title = use_title
        self.handler = None
        self.app_type = None
    
    def connect(self):
        """Connect and auto-detect application type."""
        try:
            print(f"🔍 UNIVERSAL AUTOMATION SYSTEM")
            print(f"Target: '{self.app_identifier}'")
            print("="*50)
            
            # Create temporary connection to detect app type
            temp_automation = BaseWindowAutomation(self.app_identifier, self.use_title)
            if not temp_automation.connect():
                return False
            
            detected_type = temp_automation.app_type
            temp_automation.disconnect()
            
            # Create specialized handler based on detected type
            if detected_type == 'java':
                print("🎯 Creating Java automation handler")
                self.handler = JavaWindowAutomation(self.app_identifier, self.use_title)
            elif detected_type in ['dotnet_wpf', 'dotnet_winforms', 'uwp']:
                print("🎯 Creating .NET automation handler")
                self.handler = DotNetWindowAutomation(self.app_identifier, self.use_title)
            elif detected_type in ['win32', 'win32_dialog']:
                print("🎯 Creating Win32 automation handler")
                self.handler = Win32WindowAutomation(self.app_identifier, self.use_title)
            else:
                print(f"🎯 Unknown app type '{detected_type}', using Win32 handler as fallback")
                self.handler = Win32WindowAutomation(self.app_identifier, self.use_title)
            
            # Connect with specialized handler
            if self.handler.connect():
                self.app_type = self.handler.app_type
                print(f"✅ Universal automation connected! Type: {self.app_type}")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Universal automation failed: {e}")
            return False
    
    def navigate_menu(self, menu_path, target_item):
        """Navigate menu using appropriate handler."""
        if self.handler:
            return self.handler.navigate_menu(menu_path, target_item)
        return False
    
    def identify_dialog(self, wait_timeout=5):
        """Identify dialog using appropriate handler."""
        if self.handler:
            return self.handler.identify_dialog_elements(wait_timeout)
        return {'type': 'none'}
    
    def fill_form(self, input_data):
        """Fill form using appropriate handler."""
        if self.handler:
            return self.handler.fill_form_inputs(input_data)
        return False
    
    def disconnect(self):
        """Disconnect from application."""
        if self.handler:
            self.handler.cleanup_dialogs()
            self.handler.disconnect()


# Convenience functions for the modular approach
def connect_to_application(app_title):
    """Connect to application with auto-detection."""
    automation = UniversalWindowAutomation(app_title, use_title=True)
    if automation.connect():
        return automation
    return None

def navigate_menu_and_select(automation, menu_path, target_item):
    """Navigate menu and select item."""
    return automation.navigate_menu(menu_path, target_item)

def identify_dialog_type(automation, wait_timeout=5):
    """Identify dialog type."""
    return automation.identify_dialog(wait_timeout)

def fill_form_inputs(automation, input_data):
    """Fill form inputs."""
    return automation.fill_form(input_data)

def cleanup_and_disconnect(automation):
    """Clean up and disconnect."""
    automation.disconnect() 