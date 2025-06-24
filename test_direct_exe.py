"""Test script for launching application directly via its exe."""
from windows_automation import WindowsAutomation
import time

# Application path
# APP_PATH = r"D:\cursor\simple-automation\windowsapp\dist\SimpleAutomation.exe"
APP_PATH = r"C:\Program Files\Notepad++\notepad++.exe"

def test_menu_navigation():
    """Test launching the app and navigating menus."""
    print(f"Testing application: {APP_PATH}")
    
    # Using 'with' statement for automatic cleanup
    with WindowsAutomation(app_path=APP_PATH) as automation:
        print("\nApplication should now be launching...")
        time.sleep(0.5)  # Brief moment to initialize
        
        # Test menu paths
        menu_tests = [
            ["File", "New"],
            ["Edit", "Copy"],
            ["View", "Show Symbol", "Show White Space and TAB"]  # Testing deeper menu
        ]
        
        for menu_path in menu_tests:
            print(f"\nTesting menu path: {' -> '.join(menu_path)}")
            try:
                automation.navigate_menu(menu_path)
                time.sleep(0.2)  # Brief pause between operations
            except Exception as e:
                print(f"Navigation failed: {e}")
        
        print("\nTests completed.")

if __name__ == "__main__":
    try:
        test_menu_navigation()
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting steps:")
        print("1. Verify the exe path is correct")
        print("2. Make sure WinAppDriver is running as Administrator")
        print("3. Enable Developer Mode in Windows settings")
        print("4. Try running the application manually first to ensure it works") 