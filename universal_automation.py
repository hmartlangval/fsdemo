"""Universal Windows Application Automation System.

This module provides a centralized automation framework that can handle different
types of Windows applications (Java, .NET, Win32, etc.) through auto-detection
and specialized handlers.
"""

import time
import re
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from windows_automation import WindowsAutomation


class NavigationParser:
    """Global parser for navigation paths with keyboard codes and text."""
    
    @staticmethod
    def parse_navigation_path(navigation_path):
        """Parse navigation path with curly bracket notation.
        
        Args:
            navigation_path: Navigation string like:
                - "{Alt+F} -> {N}" (keyboard codes only)
                - "{Alt+F} -> Create Project" (mixed)
                - "File -> New Project" (text only)
                - "{Ctrl+N}" (single shortcut)
                - "{Down 3}" (repeat key)
                
        Returns:
            List of step dictionaries with 'type' and 'value' keys
        """
        try:
            print(f"🔍 Parsing navigation: '{navigation_path}'")
            
            # Split by arrow notation
            parts = [part.strip() for part in navigation_path.split('->')]
            steps = []
            
            for part in parts:
                step = NavigationParser._parse_single_step(part)
                if step:
                    steps.append(step)
                    print(f"  📝 Parsed step: {step}")
            
            return steps
            
        except Exception as e:
            print(f"⚠️ Error parsing navigation path: {e}")
            return []
    
    @staticmethod
    def _parse_single_step(step_text):
        """Parse a single navigation step.
        
        Args:
            step_text: Single step like "{Alt+F}", "{N}", "{Down 2}", "Create Project"
            
        Returns:
            Dict with step information
        """
        step_text = step_text.strip()
        
        # Check if it's a keyboard code (wrapped in curly brackets)
        if step_text.startswith('{') and step_text.endswith('}'):
            code_content = step_text[1:-1]  # Remove { and }
            return NavigationParser._parse_keyboard_code(code_content)
        
        # Check if it's a menu name (common menu names)
        menu_names = ['file', 'edit', 'view', 'format', 'tools', 'help', 'window', 'actions', 'configuration']
        if step_text.lower() in menu_names:
            return {
                'type': 'menu_text',
                'value': step_text.lower(),
                'original': step_text,
                'description': f"Find menu: '{step_text}'"
            }
        
        # Otherwise, it's a menu item text
        return {
            'type': 'menu_item_text',
            'value': step_text.lower(),
            'original': step_text,
            'description': f"Find menu item: '{step_text}'"
        }
    
    @staticmethod
    def _parse_keyboard_code(code_content):
        """Parse keyboard code content (without curly brackets).
        
        Args:
            code_content: Content like "Alt+F", "N", "Down 3", "Ctrl+Shift+S"
            
        Returns:
            Dict with keyboard code information
        """
        code_content = code_content.strip()
        
        # Check for repeat patterns like "Down 3", "Up 2", "Tab 5"
        repeat_match = re.match(r'^(Down|Up|Left|Right|Tab|Enter|Escape)\s+(\d+)$', code_content, re.IGNORECASE)
        if repeat_match:
            key_name = repeat_match.group(1).lower()
            repeat_count = int(repeat_match.group(2))
            return {
                'type': 'key_repeat',
                'key': key_name,
                'count': repeat_count,
                'original': code_content,
                'description': f"Press {key_name} {repeat_count} times"
            }
        
        # Check for modifier combinations like "Alt+F", "Ctrl+N", "Ctrl+Shift+S"
        if '+' in code_content:
            parts = [part.strip() for part in code_content.split('+')]
            modifiers = []
            key = None
            
            for part in parts:
                part_lower = part.lower()
                if part_lower in ['ctrl', 'alt', 'shift', 'win']:
                    modifiers.append(part_lower)
                else:
                    key = part_lower
            
            if key:
                return {
                    'type': 'key_combination',
                    'modifiers': modifiers,
                    'key': key,
                    'original': code_content,
                    'description': f"Press {' + '.join(modifiers + [key])}"
                }
        
        # Single key press
        return {
            'type': 'key_single',
            'key': code_content.lower(),
            'original': code_content,
            'description': f"Press key: '{code_content}'"
        }
    
    @staticmethod
    def execute_step(step, automation_driver):
        """Execute a parsed navigation step.
        
        Args:
            step: Step dictionary from parse_navigation_path
            automation_driver: WebDriver instance
            
        Returns:
            bool: Success/failure
        """
        try:
            print(f"  🎯 Executing: {step['description']}")
            actions = ActionChains(automation_driver)
            
            if step['type'] == 'key_single':
                # Map special keys to Selenium Keys
                key_map = {
                    'enter': Keys.ENTER,
                    'escape': Keys.ESCAPE,
                    'tab': Keys.TAB,
                    'space': Keys.SPACE,
                    'backspace': Keys.BACKSPACE,
                    'delete': Keys.DELETE,
                    'home': Keys.HOME,
                    'end': Keys.END,
                    'pageup': Keys.PAGE_UP,
                    'pagedown': Keys.PAGE_DOWN,
                    'f1': Keys.F1, 'f2': Keys.F2, 'f3': Keys.F3, 'f4': Keys.F4,
                    'f5': Keys.F5, 'f6': Keys.F6, 'f7': Keys.F7, 'f8': Keys.F8,
                    'f9': Keys.F9, 'f10': Keys.F10, 'f11': Keys.F11, 'f12': Keys.F12
                }
                
                selenium_key = key_map.get(step['key'], step['key'])
                actions.send_keys(selenium_key).perform()
                time.sleep(0.3)
                return True
                
            elif step['type'] == 'key_combination':
                # Press modifiers down
                for modifier in step['modifiers']:
                    if modifier == 'ctrl':
                        actions.key_down(Keys.CONTROL)
                    elif modifier == 'alt':
                        actions.key_down(Keys.ALT)
                    elif modifier == 'shift':
                        actions.key_down(Keys.SHIFT)
                
                # Press main key
                actions.send_keys(step['key'])
                
                # Release modifiers
                for modifier in reversed(step['modifiers']):
                    if modifier == 'ctrl':
                        actions.key_up(Keys.CONTROL)
                    elif modifier == 'alt':
                        actions.key_up(Keys.ALT)
                    elif modifier == 'shift':
                        actions.key_up(Keys.SHIFT)
                
                actions.perform()
                time.sleep(0.5)
                return True
                
            elif step['type'] == 'key_repeat':
                key_map = {
                    'down': Keys.ARROW_DOWN,
                    'up': Keys.ARROW_UP,
                    'left': Keys.ARROW_LEFT,
                    'right': Keys.ARROW_RIGHT,
                    'tab': Keys.TAB,
                    'enter': Keys.ENTER,
                    'escape': Keys.ESCAPE
                }
                
                selenium_key = key_map.get(step['key'])
                if selenium_key:
                    for i in range(step['count']):
                        actions.send_keys(selenium_key).perform()
                        time.sleep(0.2)
                    return True
                else:
                    print(f"  ❌ Unknown repeat key: {step['key']}")
                    return False
                    
            elif step['type'] in ['menu_text', 'menu_item_text']:
                # These need to be handled by the specific automation handlers
                # Return True to indicate parsing success, actual execution happens elsewhere
                return True
                
            else:
                print(f"  ❌ Unknown step type: {step['type']}")
                return False
                
        except Exception as e:
            print(f"  ❌ Step execution failed: {e}")
            return False


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
    def navigate_menu(self, navigation_path):
        """Navigate through menu structure using the global parser.
        
        Args:
            navigation_path: Navigation string with curly bracket notation like:
                - "{Alt+F} -> {N}" (keyboard codes only)
                - "{Alt+F} -> Create Project" (mixed)
                - "File -> New Project" (text only)
                - "{Ctrl+N}" (single shortcut)
                - "{Down 3}" (repeat key)
            
        Returns:
            bool: Success/failure
        """
        try:
            print(f"\n=== BASE NAVIGATION HANDLER ===")
            print(f"App Type: {self.app_type}")
            print(f"Navigation Path: '{navigation_path}'")
            
            # Use global parser to parse the navigation path
            parsed_steps = NavigationParser.parse_navigation_path(navigation_path)
            
            if not parsed_steps:
                print(f"❌ Could not parse navigation path: '{navigation_path}'")
                return False
            
            # Execute navigation steps based on app type
            for step_index, step in enumerate(parsed_steps):
                print(f"\n📍 Step {step_index + 1}: {step['description']}")
                
                if not self._execute_navigation_step(step):
                    print(f"❌ Step {step_index + 1} failed")
                    return False
                
                # Brief pause between steps
                time.sleep(0.3)
            
            # Check for success only after ALL steps are completed
            time.sleep(0.2)  # Brief wait for any windows/dialogs to appear
            if self._check_navigation_success():
                print(f"✅ Navigation successful - change detected!")
                return True
            else:
                print(f"✅ Navigation completed - no change detected")
                return True  # Still consider successful even if no change appears
            
        except Exception as e:
            print(f"❌ Base navigation failed: {e}")
            return False
    
    def _execute_navigation_step(self, step):
        """Execute a single navigation step based on app type.
        
        Args:
            step: Parsed step dictionary from NavigationParser
            
        Returns:
            bool: Success/failure
        """
        try:
            # Handle keyboard codes directly (universal across all app types)
            if step['type'] in ['key_single', 'key_combination', 'key_repeat']:
                return NavigationParser.execute_step(step, self.automation.driver)
            
            # Handle text-based navigation (app-specific)
            elif step['type'] in ['menu_text', 'menu_item_text']:
                return self._execute_text_navigation(step)
            
            else:
                print(f"  ❌ Unknown step type: {step['type']}")
                return False
                
        except Exception as e:
            print(f"  ❌ Step execution failed: {e}")
            return False
    
    def _execute_text_navigation(self, step):
        """Execute text-based navigation - to be implemented by subclasses.
        
        Args:
            step: Parsed step dictionary for text navigation
            
        Returns:
            bool: Success/failure
        """
        # Default implementation for basic text navigation
        print(f"  ⚠️ Text navigation not implemented for {self.app_type}: {step['description']}")
        return False
    
    def _check_navigation_success(self):
        """Check if navigation was successful - can be overridden by subclasses.
        
        Returns:
            bool: True if navigation appears successful
        """
        try:
            # Basic success check - look for increased element count (dialog appeared)
            current_elements = len(self.get_all_elements())
            time.sleep(0.3)
            new_elements = len(self.get_all_elements())
            
            # Success if element count increased or we have many elements (dialog)
            return new_elements > current_elements or current_elements > 15
        except:
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
    
    def _execute_text_navigation(self, step):
        """Execute text-based navigation for Java applications.
        
        Args:
            step: Parsed step dictionary for text navigation
            
        Returns:
            bool: Success/failure
        """
        try:
            print(f"  🎯 Java text navigation: {step['description']}")
            
            # Handle text-based navigation (Java-specific)
            if step['type'] == 'menu_text':
                return self._execute_java_menu_open(step['original'])
            
            elif step['type'] == 'menu_item_text':
                return self._execute_java_menu_item(step['original'])
            
            else:
                print(f"  ❌ Unknown text navigation type for Java: {step['type']}")
                return False
                
        except Exception as e:
            print(f"  ❌ Java text navigation failed: {e}")
            return False
    
    def _execute_java_menu_open(self, menu_name):
        """Open Java menu using Alt+Key."""
        try:
            # Map menu names to keyboard shortcuts
            menu_shortcuts = {
                'file': 'f', 'edit': 'e', 'view': 'v', 'actions': 'a',
                'configuration': 'c', 'config': 'c', 'help': 'h',
                'tools': 't', 'window': 'w', 'format': 'o'
            }
            
            menu_key = menu_shortcuts.get(menu_name.lower())
            if not menu_key:
                print(f"  ❌ Unknown Java menu: {menu_name}")
                return False
            
            print(f"  📂 Opening Java menu: Alt+{menu_key.upper()}")
            actions = ActionChains(self.automation.driver)
            actions.key_down(Keys.ALT).send_keys(menu_key).key_up(Keys.ALT).perform()
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"  ❌ Java menu open failed: {e}")
            return False
    
    def _execute_java_menu_item(self, item_name):
        """Select Java menu item using text search."""
        try:
            print(f"  🎯 Selecting Java menu item: '{item_name}'")
            
            # Strategy 1: Try first letter
            if self._try_first_letter_selection(item_name.lower(), None):
                return True
            
            # Strategy 2: Try position-based navigation
            if self._try_position_based_selection(item_name, None):
                return True
            
            print(f"  ❌ Java menu item '{item_name}' not found")
            return False
            
        except Exception as e:
            print(f"  ❌ Java menu item selection failed: {e}")
            return False
    

    

    
    def _try_first_letter_selection(self, item_text, actions):
        """Try selecting menu item by first letter."""
        try:
            first_letter = item_text[0] if item_text else ''
            if first_letter:
                print(f"    Trying first letter: '{first_letter}'")
                actions.send_keys(first_letter).perform()
                time.sleep(0.5)
                return True
            return False
        except:
            return False
    
    def _try_position_based_selection(self, original_text, actions):
        """Try selecting menu item by navigating positions."""
        try:
            print(f"    Trying position-based selection...")
            max_attempts = 10
            
            for pos in range(max_attempts):
                # Press Enter to try current position
                actions.send_keys(Keys.ENTER).perform()
                time.sleep(0.3)
                
                if self._check_success_condition():
                    print(f"    ✅ Position {pos + 1} worked!")
                    return True
                
                # Move to next position
                actions.send_keys(Keys.ARROW_DOWN).perform()
                time.sleep(0.2)
            
            return False
        except:
            return False
    

    
    def _check_navigation_success(self):
        """Check if navigation was successful (dialog appeared) - Java override."""
        try:
            current_elements = len(self.get_all_elements())
            time.sleep(0.3)
            new_elements = len(self.get_all_elements())
            
            # Success if element count increased (dialog appeared)
            return new_elements > current_elements or current_elements > 15
        except:
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
    
    def _execute_text_navigation(self, step):
        """Execute text-based navigation for .NET applications.
        
        Args:
            step: Parsed step dictionary for text navigation
            
        Returns:
            bool: Success/failure
        """
        try:
            print(f"  🎯 .NET text navigation: {step['description']}")
            
            # Handle text-based navigation (.NET-specific)
            if step['type'] == 'menu_text':
                return self._execute_dotnet_menu_open(step['original'])
            
            elif step['type'] == 'menu_item_text':
                return self._execute_dotnet_menu_item(step['original'])
            
            else:
                print(f"  ❌ Unknown text navigation type for .NET: {step['type']}")
                return False
                
        except Exception as e:
            print(f"  ❌ .NET text navigation failed: {e}")
            return False
    
    def _execute_dotnet_menu_open(self, menu_name):
        """Open .NET menu using UI Automation."""
        try:
            print(f"  📂 Opening .NET menu: '{menu_name}'")
            # Try to find menu by name using UI Automation
            menu_xpath = f"//MenuItem[@Name='{menu_name}' or contains(@Name, '{menu_name}')]"
            try:
                menu_element = self.automation.driver.find_element_by_xpath(menu_xpath)
                menu_element.click()
                time.sleep(0.5)
                return True
            except:
                print(f"  ⚠️ Menu '{menu_name}' not found via UI, trying Alt+Key fallback")
                # Fallback to keyboard shortcuts
                menu_shortcuts = {
                    'file': 'f', 'edit': 'e', 'view': 'v', 'tools': 't',
                    'help': 'h', 'window': 'w', 'format': 'o'
                }
                menu_key = menu_shortcuts.get(menu_name.lower())
                if menu_key:
                    actions = ActionChains(self.automation.driver)
                    actions.key_down(Keys.ALT).send_keys(menu_key).key_up(Keys.ALT).perform()
                    time.sleep(0.5)
                    return True
                return False
        except Exception as e:
            print(f"  ❌ .NET menu open failed: {e}")
            return False
    
    def _execute_dotnet_menu_item(self, item_name):
        """Select .NET menu item using UI Automation."""
        try:
            print(f"  🎯 Selecting .NET menu item: '{item_name}'")
            # Try to find menu item by name
            item_xpath = f"//MenuItem[@Name='{item_name}' or contains(@Name, '{item_name}')]"
            try:
                item_element = self.automation.driver.find_element_by_xpath(item_xpath)
                item_element.click()
                time.sleep(0.5)
                return True
            except:
                print(f"  ⚠️ Menu item '{item_name}' not found via UI, trying first letter")
                # Fallback to first letter
                first_letter = item_name[0].lower() if item_name else ''
                if first_letter:
                    actions = ActionChains(self.automation.driver)
                    actions.send_keys(first_letter).perform()
                    time.sleep(0.3)
                    return True
                return False
        except Exception as e:
            print(f"  ❌ .NET menu item selection failed: {e}")
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
    
    def _check_navigation_success(self):
        """Check if navigation was successful - Win32 override for better window detection."""
        try:
            # For Win32 apps, do a quick check for new windows or dialogs
            initial_elements = len(self.get_all_elements())
            time.sleep(0.1)  # Minimal wait for changes to settle
            
            # Quick check for new windows by title (most reliable for Notepad)
            try:
                from window_discovery import find_window_handle_by_title
                windows = find_window_handle_by_title("Untitled - Notepad")
                if len(windows) > 1:  # Multiple Notepad windows = new window opened
                    print(f"  🔍 Win32: Detected new window (multiple Notepad instances)")
                    return True
            except:
                pass
            
            # Quick element count check
            current_elements = len(self.get_all_elements())
            if current_elements > initial_elements + 5:
                print(f"  🔍 Win32: Detected significant UI change ({initial_elements} → {current_elements} elements)")
                return True
            
            # One more quick check after brief pause
            time.sleep(0.1)
            final_elements = len(self.get_all_elements())
            if final_elements != initial_elements:
                print(f"  🔍 Win32: Basic change detected ({initial_elements} → {final_elements} elements)")
                return True
            
            return False
        except:
            return False
    
    def _execute_text_navigation(self, step):
        """Execute text-based navigation for Win32 applications.
        
        Args:
            step: Parsed step dictionary for text navigation
            
        Returns:
            bool: Success/failure
        """
        try:
            print(f"  🎯 Win32 text navigation: {step['description']}")
            
            # Handle text-based navigation (Win32-specific)
            if step['type'] == 'menu_text':
                return self._try_win32_menu_ui(step['original'])
            
            elif step['type'] == 'menu_item_text':
                return self._try_win32_menuitem_ui(step['original'])
            
            else:
                print(f"  ❌ Unknown text navigation type for Win32: {step['type']}")
                return False
                
        except Exception as e:
            print(f"  ❌ Win32 text navigation failed: {e}")
            return False
    

    
    def _try_win32_menu_ui(self, menu_name):
        """Try opening menu using UI Automation."""
        try:
            menu_xpath = f"//Menu[@Name='{menu_name}' or contains(@Name, '{menu_name}')]"
            main_menu = self.automation.driver.find_element_by_xpath(menu_xpath)
            print(f"  ✅ Found menu via UI: {menu_name}")
            main_menu.click()
            time.sleep(0.5)
            return True
        except:
            print(f"  ⚠️ UI menu access failed for: {menu_name}")
            return False
    
    def _try_win32_menuitem_ui(self, item_name):
        """Try selecting menu item using UI Automation."""
        try:
            item_xpath = f"//MenuItem[@Name='{item_name}' or contains(@Name, '{item_name}')]"
            menu_item = self.automation.driver.find_element_by_xpath(item_xpath)
            print(f"  ✅ Found menu item via UI: {item_name}")
            menu_item.click()
            time.sleep(0.5)
            return True
        except:
            print(f"  ⚠️ UI menu item access failed for: {item_name}")
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
    
    def navigate_menu(self, navigation_path):
        """Navigate menu using appropriate handler."""
        if self.handler:
            return self.handler.navigate_menu(navigation_path)
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

def navigate_menu_and_select(automation, navigation_path):
    """Navigate menu and select item."""
    return automation.navigate_menu(navigation_path)

def identify_dialog_type(automation, wait_timeout=5):
    """Identify dialog type."""
    return automation.identify_dialog(wait_timeout)

def fill_form_inputs(automation, input_data):
    """Fill form inputs."""
    return automation.fill_form(input_data)

def cleanup_and_disconnect(automation):
    """Clean up and disconnect."""
    automation.disconnect() 