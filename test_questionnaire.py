"""Test script for questionnaire navigation."""
from windows_automation import WindowsAutomation
import time

# Application path
APP_PATH = r"D:\cursor\simple-automation\windowsapp\dist\SimpleAutomation.exe"

def test_questionnaire_navigation():
    """Test navigating through questionnaire pages."""
    print(f"Testing questionnaire navigation in: {APP_PATH}")
    
    with WindowsAutomation(app_path=APP_PATH) as automation:
        # Wait for application to initialize
        automation.wait_for_element("Questionnaire Tree", timeout=2)
        
        # Select questionnaire in treeview
        automation.select_treeview_item("Basic Questionnaire")
        
        # Navigate through pages
        for page in range(1, 16):  # 15 pages
            print(f"\nProcessing page {page}")
            
            # Wait for page to load
            if not automation.wait_for_element(f"Page {page}", timeout=2):
                print(f"Page {page} not found or not loaded")
                continue
            
            # Fill form fields (example)
            automation.fill_form_field("Name", f"Test User {page}")
            automation.fill_form_field("Comments", f"Test comment for page {page}")
            
            # Click Next
            if not automation.click_button("Next"):
                print("Could not find Next button")
                break
            
            # Brief pause between pages (can be adjusted)
            time.sleep(0.2)
        
        print("\nQuestionnaire navigation completed")

if __name__ == "__main__":
    try:
        test_questionnaire_navigation()
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting steps:")
        print("1. Verify the exe path is correct")
        print("2. Make sure WinAppDriver is running as Administrator")
        print("3. Enable Developer Mode in Windows settings") 