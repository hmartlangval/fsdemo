"""Simple test script to discover UI elements in a Windows application."""
import sys
import time
from windows_automation import WindowsAutomation

def wait_for_ui_elements(driver, timeout=15):
    """Wait for UI elements to be available - more robust version."""
    print(f"Waiting up to {timeout} seconds for UI to be ready...")
    start_time = time.time()
    
    # First, just wait a bit for the UI to settle after connection
    time.sleep(2)
    
    while time.time() - start_time < timeout:
        try:
            # Try a simple, safe operation first
            current_window = driver.current_window_handle
            if not current_window:
                print("Window handle lost - application may have closed")
                return False
                
            # Try to get elements
            elements = driver.find_elements_by_xpath("//*")
            element_count = len(elements)
            
            if element_count > 5:  # More than just basic window controls
                print(f"Found {element_count} elements - UI appears ready")
                return True
            else:
                print(f"Found {element_count} elements - waiting for more...")
                
        except Exception as e:
            error_msg = str(e)
            if "closed" in error_msg.lower():
                print(f"Application appears to have closed: {error_msg}")
                return False
            else:
                print(f"Waiting... (Error: {error_msg})")
        
        time.sleep(1)
    
    print("Timeout waiting for UI - proceeding anyway")
    return True  # Continue even on timeout

def get_all_elements_info(driver):
    """Get information about all UI elements - with error handling."""
    try:
        # First check if driver is still valid
        current_window = driver.current_window_handle
        if not current_window:
            print("Driver connection lost")
            return []
            
        all_elements = driver.find_elements_by_xpath("//*")
        elements_info = []
        
        print(f"Processing {len(all_elements)} elements...")
        
        for i, element in enumerate(all_elements):
            try:
                element_info = {
                    'index': i,
                    'name': element.get_attribute("Name") or "",
                    'automation_id': element.get_attribute("AutomationId") or "",
                    'class_name': element.get_attribute("ClassName") or "",
                    'control_type': element.get_attribute("ControlType") or "",
                    'localized_control_type': element.get_attribute("LocalizedControlType") or "",
                    'is_enabled': element.get_attribute("IsEnabled") or "",
                    'is_visible': element.get_attribute("IsOffscreen") != "True",
                    'bounding_rectangle': element.get_attribute("BoundingRectangle") or "",
                    'text': element.text or "",
                    'is_keyboard_focusable': element.get_attribute("IsKeyboardFocusable") or ""
                }
                elements_info.append(element_info)
            except Exception as e:
                print(f"Error getting info for element {i}: {e}")
                continue
                
        return elements_info
    except Exception as e:
        print(f"Error getting elements: {e}")
        return []

def print_interactive_elements(elements_info):
    """Print only potentially interactive elements."""
    interactive_types = [
        'MenuItem', 'Button', 'ToolBar', 'MenuBar', 'Menu', 'ComboBox',
        'Edit', 'Text', 'TreeItem', 'ListItem', 'TabItem', 'CheckBox',
        'RadioButton', 'Slider', 'ScrollBar', 'SplitButton', 'ToggleButton'
    ]
    
    print("\n=== INTERACTIVE ELEMENTS ===")
    interactive_elements = [e for e in elements_info if any(t in e.get('control_type', '') for t in interactive_types)]
    
    if not interactive_elements:
        print("No interactive elements found!")
        return
    
    for element in interactive_elements:
        print(f"\nElement {element['index']}:")
        print(f"  Name: '{element['name']}'")
        print(f"  ControlType: '{element['control_type']}'")
        print(f"  ClassName: '{element['class_name']}'")
        print(f"  AutomationId: '{element['automation_id']}'")
        print(f"  IsEnabled: {element['is_enabled']}")
        print(f"  IsVisible: {element['is_visible']}")
        print(f"  Text: '{element['text']}'")
        print(f"  BoundingRectangle: {element['bounding_rectangle']}")

def print_all_elements(elements_info):
    """Print all elements for complete debugging."""
    print("\n=== ALL ELEMENTS ===")
    for element in elements_info:
        print(f"\nElement {element['index']}:")
        print(f"  Name: '{element['name']}'")
        print(f"  ControlType: '{element['control_type']}'")
        print(f"  ClassName: '{element['class_name']}'")
        print(f"  AutomationId: '{element['automation_id']}'")
        print(f"  LocalizedControlType: '{element['localized_control_type']}'")
        print(f"  IsEnabled: {element['is_enabled']}")
        print(f"  IsVisible: {element['is_visible']}")
        print(f"  Text: '{element['text']}'")
        print(f"  BoundingRectangle: {element['bounding_rectangle']}")
        print(f"  IsKeyboardFocusable: {element['is_keyboard_focusable']}")

def search_for_menu_keywords(elements_info):
    """Search for elements that might be menus based on keywords."""
    menu_keywords = ['file', 'edit', 'actions', 'configuration', 'help', 'view', 'tools', 'options']
    
    print("\n=== POTENTIAL MENU ELEMENTS (by keyword) ===")
    found_any = False
    
    for element in elements_info:
        name_lower = element['name'].lower()
        text_lower = element['text'].lower()
        
        for keyword in menu_keywords:
            if keyword in name_lower or keyword in text_lower:
                found_any = True
                print(f"\nFound potential menu element:")
                print(f"  Name: '{element['name']}'")
                print(f"  Text: '{element['text']}'")
                print(f"  ControlType: '{element['control_type']}'")
                print(f"  ClassName: '{element['class_name']}'")
                print(f"  AutomationId: '{element['automation_id']}'")
                print(f"  IsEnabled: {element['is_enabled']}")
                print(f"  BoundingRectangle: {element['bounding_rectangle']}")
                break
    
    if not found_any:
        print("No elements found with common menu keywords")

def main():
    # Change this to match your application window title
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--title', default="Untitled - Notepad", help="Window title to connect to")
    args = parser.parse_args()
    APP_TITLE = args.title
    
    print(f"Connecting to application with title containing: '{APP_TITLE}'")
    
    try:
        # Connect to the application
        automation = WindowsAutomation(APP_TITLE, use_title=True)
        automation.connect()
        
        print("Successfully connected!")
        
        # Check if connection is still valid
        try:
            window_handle = automation.driver.current_window_handle
            print(f"Current window handle: {window_handle}")
        except Exception as e:
            print(f"Warning: Could not get window handle: {e}")
        
        # Wait for UI to be ready (with better error handling)
        ui_ready = wait_for_ui_elements(automation.driver, timeout=15)
        
        if not ui_ready:
            print("UI readiness check failed, but continuing...")
        
        # Get all elements information
        print("Discovering all UI elements...")
        elements_info = get_all_elements_info(automation.driver)
        
        if not elements_info:
            print("No elements found - application may have closed or connection lost")
            return
        
        print(f"Total elements found: {len(elements_info)}")
        
        # Print interactive elements
        print_interactive_elements(elements_info)
        
        # Search for menu keywords
        search_for_menu_keywords(elements_info)
        
        # Ask user if they want to see all elements
        print(f"\nFound {len(elements_info)} total elements.")
        show_all = input("Do you want to see ALL elements? (y/n): ").lower().strip()
        if show_all == 'y':
            print_all_elements(elements_info)
        
        # Disconnect
        automation.disconnect()
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure:")
        print("1. WinAppDriver is running (WinAppDriver.exe)")
        print("2. The application is open and visible")
        print("3. The window title matches what you specified")
        print("4. The application is not closing itself during automation")

if __name__ == "__main__":
    main() 