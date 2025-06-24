"""Test script for Fiserv application automation."""
import argparse
from window_discovery import discover_windows
from windows_automation import WindowsAutomation
import time

# Application path
# APP_PATH = r"D:\cursor\simple-automation\windowsapp\dist\SimpleAutomation.exe"
APP_PATH = r"C:\Windows\System32\notepad.exe"
APP_TITLE = "Untitled - Notepad"

def navigate_menu_path(menu_path):
    """Navigate through the specified menu path."""
    print(f"Testing menu navigation: {' -> '.join(menu_path)}")
    
    # with WindowsAutomation(app_identifier=APP_PATH, use_title=False) as automation:
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
    # Example menu path - this should be provided as input
    # test_menu_path = ["Dev Test", "Questionnaire"]
    test_menu_path = ["File", "New tab"]
    
    try:
        navigate_menu_path(test_menu_path)
    except Exception as e:
        print(f"\nError: {e}")