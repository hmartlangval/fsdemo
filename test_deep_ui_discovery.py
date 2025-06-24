"""Enhanced UI discovery script for Java applications with modular functions."""
import sys
import time
from windows_automation import WindowsAutomation
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

def connect_to_application(app_title):
    """Connect to the application and return automation instance.
    
    Args:
        app_title: Window title to connect to
        
    Returns:
        WindowsAutomation instance or None if failed
    """
    try:
        print(f"=== CONNECTING TO APPLICATION ===")
        print(f"Connecting to: '{app_title}'")
        
        automation = WindowsAutomation(app_title, use_title=True)
        automation.connect()
        
        print("✅ Successfully connected to application!")
        return automation
        
    except Exception as e:
        print(f"❌ Failed to connect to application: {e}")
        return None

def navigate_menu_and_select(automation, target_menu_item, menu_shortcut="alt+f"):
    """Navigate through Java Swing menu and select target item.
    
    Args:
        automation: WindowsAutomation instance
        target_menu_item: Text of the menu item to find (e.g., "New", "Open", etc.)
        menu_shortcut: Keyboard shortcut to open menu (default: "alt+f")
        
    Returns:
        bool: True if menu item was found and selected, False otherwise
    """
    try:
        print(f"\n=== NAVIGATING MENU ===")
        print(f"Opening menu with: {menu_shortcut}")
        print(f"Looking for menu item: '{target_menu_item}'")
        
        # Step 1: Open the menu using shortcut
        actions = ActionChains(automation.driver)
        
        # Parse the shortcut (e.g., "alt+f")
        parts = menu_shortcut.lower().split('+')
        if len(parts) == 2 and parts[0] == 'alt':
            actions.key_down(Keys.ALT).send_keys(parts[1]).key_up(Keys.ALT).perform()
        else:
            print(f"❌ Unsupported menu shortcut format: {menu_shortcut}")
            return False
            
        time.sleep(1)  # Wait for menu to appear
        
        # Step 2: Navigate through menu items using arrow keys
        print(f"Searching through menu items...")
        max_attempts = 15  # Maximum number of arrow key presses
        found_item = False
        
        for attempt in range(max_attempts):
            try:
                # Get the currently focused element text
                current_text = automation.get_active_element_text()
                print(f"  [{attempt + 1}] Current: '{current_text}'")
                
                # Check if we found our target (case-insensitive partial match)
                if target_menu_item.lower() in current_text.lower():
                    print(f"  ✅ Found target menu item: '{current_text}'")
                    found_item = True
                    break
                
                # Press Down arrow to move to next menu item
                actions.send_keys(Keys.ARROW_DOWN).perform()
                time.sleep(0.3)  # Small delay between navigation
                
            except Exception as e:
                print(f"  ⚠️ Error during menu navigation: {e}")
                continue
        
        if not found_item:
            print(f"❌ Could not find menu item '{target_menu_item}' after {max_attempts} attempts")
            # Close menu
            actions.send_keys(Keys.ESCAPE).perform()
            return False
        
        # Step 3: Press Enter to select the menu item
        print("Pressing Enter to select menu item...")
        actions.send_keys(Keys.ENTER).perform()
        time.sleep(1)  # Brief pause after selection
        
        print("✅ Menu navigation completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error in menu navigation: {e}")
        # Try to close menu
        try:
            actions = ActionChains(automation.driver)
            actions.send_keys(Keys.ESCAPE).perform()
        except:
            pass
        return False

def identify_dialog_type(automation, wait_timeout=5):
    """Scan and identify what type of dialog/screen appeared.
    
    Args:
        automation: WindowsAutomation instance
        wait_timeout: Maximum time to wait for dialog to appear
        
    Returns:
        dict: Information about the detected dialog type and elements
              Format: {
                  'type': 'two_input_form' | 'single_input_form' | 'button_dialog' | 'unknown' | 'none',
                  'elements': [...],
                  'input_fields': [...],
                  'buttons': [...],
                  'description': 'Human readable description'
              }
    """
    try:
        print(f"\n=== IDENTIFYING DIALOG TYPE ===")
        print(f"Waiting up to {wait_timeout} seconds for dialog to appear...")
        
        # Get baseline element count
        initial_elements = automation.driver.find_elements_by_xpath("//*")
        initial_count = len(initial_elements)
        print(f"Initial element count: {initial_count}")
        
        # Wait for dialog to appear
        dialog_appeared = False
        for wait_attempt in range(wait_timeout * 2):  # Check every 0.5 seconds
            try:
                current_elements = automation.driver.find_elements_by_xpath("//*")
                current_count = len(current_elements)
                
                # If significantly more elements appeared, likely a dialog
                if current_count > initial_count + 3:
                    dialog_appeared = True
                    print(f"✅ Dialog detected! Element count: {initial_count} → {current_count}")
                    break
                    
            except Exception as e:
                print(f"  ⚠️ Error checking for dialog: {e}")
            
            time.sleep(0.5)
        
        if not dialog_appeared:
            return {
                'type': 'none',
                'elements': [],
                'input_fields': [],
                'buttons': [],
                'description': 'No dialog detected'
            }
        
        # Wait a bit more for dialog to fully load
        time.sleep(1)
        
        # Analyze the dialog
        print("Analyzing dialog elements...")
        
        # Get all current elements
        all_elements = automation.driver.find_elements_by_xpath("//*")
        
        # Find input fields
        input_fields = []
        input_strategies = [
            ("Edit controls", "//Edit"),
            ("Text inputs", "//Text[@IsKeyboardFocusable='true']"),
            ("ComboBox controls", "//ComboBox"),
        ]
        
        for strategy_name, xpath in input_strategies:
            try:
                found_inputs = automation.driver.find_elements_by_xpath(xpath)
                for input_elem in found_inputs:
                    try:
                        control_type = input_elem.get_attribute("ControlType")
                        name = input_elem.get_attribute("Name") or ""
                        is_focusable = input_elem.get_attribute("IsKeyboardFocusable")
                        bounding_rect = input_elem.get_attribute("BoundingRectangle")
                        
                        if is_focusable == "true":
                            input_fields.append({
                                'element': input_elem,
                                'name': name,
                                'type': control_type,
                                'rect': bounding_rect,
                                'strategy': strategy_name
                            })
                            print(f"  📝 Input field: '{name}' ({control_type})")
                            
                    except Exception as e:
                        continue
                        
            except Exception as e:
                print(f"  ⚠️ Strategy {strategy_name} failed: {e}")
                continue
        
        # Find buttons
        buttons = []
        try:
            button_elements = automation.driver.find_elements_by_xpath("//Button")
            for button_elem in button_elements:
                try:
                    name = button_elem.get_attribute("Name") or ""
                    is_enabled = button_elem.get_attribute("IsEnabled")
                    bounding_rect = button_elem.get_attribute("BoundingRectangle")
                    
                    buttons.append({
                        'element': button_elem,
                        'name': name,
                        'enabled': is_enabled,
                        'rect': bounding_rect
                    })
                    print(f"  🔘 Button: '{name}' (Enabled: {is_enabled})")
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"  ⚠️ Error finding buttons: {e}")
        
        # Determine dialog type based on analysis
        dialog_info = {
            'elements': all_elements,
            'input_fields': input_fields,
            'buttons': buttons,
        }
        
        # Classification logic
        if len(input_fields) >= 2:
            dialog_info['type'] = 'two_input_form'
            dialog_info['description'] = f'Two-input form dialog with {len(input_fields)} input fields and {len(buttons)} buttons'
            print(f"✅ Identified as: TWO_INPUT_FORM")
        elif len(input_fields) == 1:
            dialog_info['type'] = 'single_input_form'
            dialog_info['description'] = f'Single-input form dialog with {len(input_fields)} input field and {len(buttons)} buttons'
            print(f"✅ Identified as: SINGLE_INPUT_FORM")
        elif len(buttons) > 0:
            dialog_info['type'] = 'button_dialog'
            dialog_info['description'] = f'Button-only dialog with {len(buttons)} buttons'
            print(f"✅ Identified as: BUTTON_DIALOG")
        else:
            dialog_info['type'] = 'unknown'
            dialog_info['description'] = f'Unknown dialog type with {len(all_elements)} total elements'
            print(f"❓ Identified as: UNKNOWN")
        
        print(f"Dialog analysis complete: {dialog_info['description']}")
        return dialog_info
        
    except Exception as e:
        print(f"❌ Error identifying dialog type: {e}")
        return {
            'type': 'error',
            'elements': [],
            'input_fields': [],
            'buttons': [],
            'description': f'Error during analysis: {e}'
        }

def fill_two_input_form(automation, dialog_info, first_text="first input", second_text="second input", click_ok=True):
    """Fill a two-input form dialog.
    
    Args:
        automation: WindowsAutomation instance
        dialog_info: Dialog information from identify_dialog_type()
        first_text: Text for first input field
        second_text: Text for second input field
        click_ok: Whether to click OK/Submit button after filling
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"\n=== FILLING TWO-INPUT FORM ===")
        
        # Validate we have a two-input form
        if dialog_info['type'] != 'two_input_form':
            print(f"❌ Dialog type is '{dialog_info['type']}', not 'two_input_form'")
            return False
        
        input_fields = dialog_info['input_fields']
        if len(input_fields) < 2:
            print(f"❌ Need at least 2 input fields, found {len(input_fields)}")
            return False
        
        print(f"Filling {len(input_fields)} input fields...")
        
        # Fill first input field
        print(f"📝 Filling first field with: '{first_text}'")
        try:
            first_field = input_fields[0]['element']
            first_field.click()  # Focus the field
            time.sleep(0.2)
            first_field.clear()  # Clear existing content
            first_field.send_keys(first_text)
            time.sleep(0.3)
            print(f"  ✅ First field filled successfully")
        except Exception as e:
            print(f"  ❌ Error filling first field: {e}")
            return False
        
        # Fill second input field
        print(f"📝 Filling second field with: '{second_text}'")
        try:
            second_field = input_fields[1]['element']
            second_field.click()  # Focus the field
            time.sleep(0.2)
            second_field.clear()  # Clear existing content
            second_field.send_keys(second_text)
            time.sleep(0.3)
            print(f"  ✅ Second field filled successfully")
        except Exception as e:
            print(f"  ❌ Error filling second field: {e}")
            return False
        
        # Click OK/Submit button if requested
        if click_ok:
            print("🔘 Looking for OK/Submit button...")
            ok_buttons = [btn for btn in dialog_info['buttons'] 
                         if any(keyword in btn['name'].lower() 
                               for keyword in ['ok', 'submit', 'apply', 'save'])]
            
            if ok_buttons:
                try:
                    ok_button = ok_buttons[0]
                    print(f"  Clicking button: '{ok_button['name']}'")
                    ok_button['element'].click()
                    time.sleep(0.5)
                    print(f"  ✅ Button clicked successfully")
                except Exception as e:
                    print(f"  ❌ Error clicking button: {e}")
                    return False
            else:
                print(f"  ⚠️ No OK/Submit button found among {len(dialog_info['buttons'])} buttons")
        
        print("✅ Two-input form filled successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error filling two-input form: {e}")
        return False

def cleanup_and_disconnect(automation):
    """Clean up any open dialogs/menus and disconnect.
    
    Args:
        automation: WindowsAutomation instance
    """
    try:
        print(f"\n=== CLEANUP AND DISCONNECT ===")
        
        if automation and automation.driver:
            # Try to close any open dialogs/menus
            print("Closing any open dialogs/menus...")
            actions = ActionChains(automation.driver)
            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(0.5)
            actions.send_keys(Keys.ESCAPE).perform()  # Double escape
            time.sleep(0.5)
            
            # Disconnect
            print("Disconnecting from application...")
            automation.disconnect()
            print("✅ Cleanup completed successfully!")
        
    except Exception as e:
        print(f"⚠️ Error during cleanup: {e}")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--title', default="Brand Test Tool", help="Window title to connect to")
    parser.add_argument('--menu-item', default="New", help="Menu item to search for (e.g., 'New', 'Open', 'Save')")
    parser.add_argument('--test-modular', action='store_true', help="Test the new modular functions")
    args = parser.parse_args()
    
    APP_TITLE = args.title
    automation = None
    
    try:
        if args.test_modular:
            # Test the new modular approach
            print(f"\n🧩 TESTING MODULAR FUNCTIONS")
            print("="*50)
            
            # Step 1: Connect
            automation = connect_to_application(APP_TITLE)
            if not automation:
                return
            
            # Step 2: Navigate menu
            if not navigate_menu_and_select(automation, args.menu_item):
                return
            
            # Step 3: Identify dialog
            dialog_info = identify_dialog_type(automation)
            print(f"\nDialog identified: {dialog_info['description']}")
            
            # Step 4: Take action based on dialog type
            if dialog_info['type'] == 'two_input_form':
                success = fill_two_input_form(automation, dialog_info, "first input", "second input")
                if success:
                    print("✅ Modular workflow completed successfully!")
                else:
                    print("❌ Failed to fill form")
            elif dialog_info['type'] == 'single_input_form':
                print("ℹ️ Single input form detected - handler can be added here")
            elif dialog_info['type'] == 'button_dialog':
                print("ℹ️ Button dialog detected - handler can be added here")
            else:
                print(f"ℹ️ Dialog type '{dialog_info['type']}' - no action taken")
                print("Tomorrow we can add handlers for other dialog types here!")
            
        else:
            print("Use --test-modular to test the modular functions")
            print("Example: python test_deep_ui_discovery.py --title 'Brand Test Tool' --menu-item 'New' --test-modular")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Always cleanup
        if automation:
            cleanup_and_disconnect(automation)

if __name__ == "__main__":
    main() 