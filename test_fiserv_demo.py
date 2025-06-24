"""Test script for Fiserv application automation."""
from windows_automation import WindowsAutomation
import time

# Application path
# APP_PATH = r"D:\cursor\simple-automation\windowsapp\dist\SimpleAutomation.exe"
APP_TITLE = "Brand Test Tool"

def navigate_menu_path(menu_path):
    """Navigate through the specified menu path."""
    print(f"Testing menu navigation: {' -> '.join(menu_path)}")
    
    with WindowsAutomation(app_identifier=APP_TITLE, use_title=True) as automation:
        print("\nApplication should now be launching...")
        time.sleep(0.5)  # Brief moment to initialize
        
        try:
            # automation.set_control_type_filter(["MenuItem"])
            automation.navigate_menu(menu_path)
            print("Menu navigation successful")
            time.sleep(0.2)  # Brief pause after navigation
            
        except Exception as e:
            print(f"\nError during navigation: {e}")

if __name__ == "__main__":

    test_menu_path = ["File", "Create Project"]
    
    try:
        navigate_menu_path(test_menu_path)
    except Exception as e:
        print(f"\nError: {e}")