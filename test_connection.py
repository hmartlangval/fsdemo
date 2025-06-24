"""Minimal test script for WinAppDriver connection."""
from appium import webdriver
import time

# Basic capabilities for testing Notepad
desired_caps = {
    "app": r"C:\Windows\System32\notepad.exe",  # Using Notepad as test app
    "platformName": "Windows",
    "deviceName": "WindowsPC"
}

# Try to connect to WinAppDriver
print("Attempting to connect to WinAppDriver...")
print(f"Using capabilities: {desired_caps}")

try:
    driver = webdriver.Remote(
        command_executor='http://127.0.0.1:4723',
        desired_capabilities=desired_caps
    )
    print("Successfully connected!")
    
    # Wait a bit
    time.sleep(5)
    
    # Clean up
    driver.quit()
    print("Test completed successfully!")
    
except Exception as e:
    print(f"Error: {e}")
    print("\nTroubleshooting steps:")
    print("1. Is WinAppDriver running as Administrator?")
    print("2. Is Developer Mode enabled in Windows settings?")
    print("3. What version of WinAppDriver are you using?") 