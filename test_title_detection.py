"""Test script for Fiserv application automation."""
import argparse
from window_discovery import discover_windows, find_window_handle_by_title
from windows_automation import WindowsAutomation
import time

# qZ&7Fv$1 -- Raj's system anydesk
# Bw3*Rt^5 - Dinesh's system anydesk

# Application title
APP_TITLE = r"AnyDesk"
DEFAULT_TITLE = "Brand Test Tool"
WINAPPDRIVER_URL = "http://127.0.0.1:4723"
COMMAND_TIMEOUT_SEC = 30

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Windows GUI Automation Demo")
    parser.add_argument("--title", default=DEFAULT_TITLE, help="Window title to automate")
    parser.add_argument("--list-windows", action="store_true", help="List available windows and exit")
    parser.add_argument("--server", default=WINAPPDRIVER_URL, help="WinAppDriver server URL")
    return parser.parse_args()

def navigate_menu_path(menu_path):
    """Navigate through the specified menu path."""
    print(f"Testing menu navigation: {' -> '.join(menu_path)}")
    window_info = find_window_handle_by_title(APP_TITLE)
    
    if not window_info:
        print(f"\nError: Could not find window with title '{APP_TITLE}'")
        print("Available windows:")
        # discover_windows()
        return
        
    print(f"Found window:")
    print(f"  Title: {window_info['title']}")
    print(f"  Handle: {window_info['hwnd']}")
    print(f"  PID: {window_info['pid']}")
    
    
if __name__ == "__main__":
    # Example menu path - this should be provided as input
    # test_menu_path = ["Dev Test", "Questionnaire"]
    test_menu_path = ["File", "New tab"]
    
    args = _parse_args()
    
    if args.list_windows:
        discover_windows()
        exit(0)
    
    try:
        navigate_menu_path(test_menu_path)
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting steps:")
        print("1. Verify the exe path is correct")
        print("2. Make sure WinAppDriver is running as Administrator")
        print("3. Enable Developer Mode in Windows settings") 