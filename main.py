"""WinAppDriver demo using Appium Python Client."""
import argparse
import signal
import sys
import time
from typing import Dict, Any

from appium import webdriver
from selenium.common.exceptions import TimeoutException

from window_discovery import find_window_handle_by_title, discover_windows

DEFAULT_TITLE = "Simple Automation"
WINAPPDRIVER_URL = "http://127.0.0.1:4723"
COMMAND_TIMEOUT_SEC = 30

# Global flag for interrupt handling
interrupted = False

def signal_handler(signum, frame):
    """Handle Ctrl+C and other signals gracefully."""
    global interrupted
    interrupted = True
    print("\nReceived interrupt signal. Cleaning up...")
    sys.exit(1)

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Windows GUI Automation Demo")
    parser.add_argument("--title", default=DEFAULT_TITLE, help="Window title to automate")
    parser.add_argument("--list-windows", action="store_true", help="List available windows and exit")
    parser.add_argument("--server", default=WINAPPDRIVER_URL, help="WinAppDriver server URL")
    return parser.parse_args()

def _build_capabilities(window_info: Dict) -> Dict[str, Any]:
    """Build WinAppDriver capabilities using window handle."""
    if not window_info:
        raise ValueError("Window information not found")
        
    caps = {
        "platformName": "Windows",
        "deviceName": "WindowsPC",
        "newCommandTimeout": COMMAND_TIMEOUT_SEC,
        "app": "Root",
        # Use the window handle directly
        "appTopLevelWindow": str(window_info['hwnd'])
    }
    
    print("\nConnecting with capabilities:")
    for key, value in caps.items():
        print(f"  {key}: {value}")
    
    return caps

def create_driver(server_url: str, capabilities: Dict[str, Any]) -> webdriver.Remote:
    """Create WebDriver connection."""
    try:
        return webdriver.Remote(
            command_executor=server_url,
            desired_capabilities=capabilities
        )
    except Exception as e:
        print(f"\nFailed to connect: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure WinAppDriver is running as Administrator")
        print("2. Verify the window is not minimized")
        print("3. Try running with --list-windows to verify the window title")
        raise

def main() -> None:
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    args = _parse_args()
    
    if args.list_windows:
        discover_windows()
        return
    
    print(f"\nLooking for window with title: {args.title}")
    window_info = find_window_handle_by_title(args.title)
    
    if not window_info:
        print(f"\nError: Could not find window with title '{args.title}'")
        print("Available windows:")
        discover_windows()
        return
        
    print(f"Found window:")
    print(f"  Title: {window_info['title']}")
    print(f"  Handle: {window_info['hwnd']}")
    print(f"  PID: {window_info['pid']}")
    
    driver = None
    try:
        caps = _build_capabilities(window_info)
        driver = create_driver(args.server, caps)
        
        print("\nSuccessfully connected to the window!")
        print("Press Ctrl+C to exit...")
        
        # Keep the session alive until user interrupts
        while not interrupted:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nOperation interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        if driver:
            try:
                print("\nClosing WebDriver session...")
                driver.quit()
            except Exception as e:
                print(f"Error while closing session: {e}")

if __name__ == "__main__":
    main()