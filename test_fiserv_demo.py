"""Test script for Fiserv application automation."""
from windows_automation import WindowsAutomation
import time

# qZ&7Fv$1 -- Raj's system anydesk
# Bw3*Rt^5 - Dinesh's system anydesk

# Application path
# APP_PATH = r"D:\cursor\simple-automation\windowsapp\dist\SimpleAutomation.exe"
APP_PATH = r"C:\Windows\System32\notepad.exe"

def navigate_menu_path(menu_path):
    """Navigate through the specified menu path."""
    print(f"Testing menu navigation: {' -> '.join(menu_path)}")
    
    with WindowsAutomation(app_path=APP_PATH) as automation:
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
        print("\nTroubleshooting steps:")
        print("1. Verify the exe path is correct")
        print("2. Make sure WinAppDriver is running as Administrator")
        print("3. Enable Developer Mode in Windows settings") 