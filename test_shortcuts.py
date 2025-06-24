"""Test script for shortcut-based navigation."""
from windows_automation import WindowsAutomation
import time

# Application path
APP_PATH = r"C:\Program Files\Notepad++\notepad++.exe"

def test_shortcut_navigation():
    """Test navigating using keyboard shortcuts."""
    print(f"Testing shortcut navigation in: {APP_PATH}")
    
    with WindowsAutomation(app_path=APP_PATH) as automation:
        # Test File -> New
        print("\nTesting File -> New")
        try:
            # First ALT+F (holding ALT and pressing F)
            automation.navigate_by_shortcut(['alt+f'])
            time.sleep(0.5)  # Wait for menu
            
            # Then just N
            automation.navigate_by_shortcut(['n'])
            
        except Exception as e:
            print(f"Error: {e}")
        
        print("Test completed")

if __name__ == "__main__":
    try:
        test_shortcut_navigation()
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting steps:")
        print("1. Verify the exe path is correct")
        print("2. Make sure WinAppDriver is running as Administrator")
        print("3. Enable Developer Mode in Windows settings") 