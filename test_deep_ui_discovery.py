"""Enhanced UI discovery script for Java applications and hard-to-detect menus."""
import sys
import time
from windows_automation import WindowsAutomation

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--title', default="Brand Test Tool", help="Window title to connect to")
    args = parser.parse_args()
    APP_TITLE = args.title
    
    print(f"Enhanced UI Discovery for: '{APP_TITLE}'")
    print("This script is designed specifically for Java applications that may not expose menus")
    
    try:
        # Connect to the application
        automation = WindowsAutomation(APP_TITLE, use_title=True)
        automation.connect()
        
        print("Successfully connected!")
        print("Java applications (SunAwtFrame) often don't expose menus through UI Automation")
        print("The menus you see (File, Actions, Configuration, Help) are likely:")
        print("1. Custom painted Java Swing components")
        print("2. Not accessible through Windows UI Automation")
        print("3. Require keyboard shortcuts or screen coordinates for automation")
        
        # Wait a moment for UI to settle
        time.sleep(2)
        
        print("\nTrying keyboard shortcuts to access menus...")
        
        # Try Alt key to activate menu
        try:
            from selenium.webdriver.common.keys import Keys
            from selenium.webdriver.common.action_chains import ActionChains
            
            actions = ActionChains(automation.driver)
            
            # Try Alt to activate menu bar
            print("Pressing Alt key...")
            actions.send_keys(Keys.ALT).perform()
            time.sleep(1)
            
            # Check if any new elements appeared
            elements_after_alt = automation.driver.find_elements_by_xpath("//*")
            print(f"Elements after Alt press: {len(elements_after_alt)}")
            
            # Try Alt+F for File menu
            print("Trying Alt+F...")
            actions.key_down(Keys.ALT).send_keys('f').key_up(Keys.ALT).perform()
            time.sleep(1)
            
            elements_after_altf = automation.driver.find_elements_by_xpath("//*")
            print(f"Elements after Alt+F: {len(elements_after_altf)}")
            
            # Press Escape to close
            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Keyboard interaction failed: {e}")
        
        print("\n" + "="*60)
        print("JAVA APPLICATION MENU ACCESS RECOMMENDATIONS:")
        print("="*60)
        print("Since this is a Java Swing application, the menus are likely not")
        print("accessible through standard Windows UI Automation. Try these approaches:")
        print()
        print("1. KEYBOARD SHORTCUTS:")
        print("   - Alt+F (File menu)")
        print("   - Alt+A (Actions menu)")  
        print("   - Alt+C (Configuration menu)")
        print("   - Alt+H (Help menu)")
        print()
        print("2. SCREEN COORDINATES:")
        print("   - Click at specific pixel coordinates where menus are located")
        print("   - Use pyautogui or similar for coordinate-based clicking")
        print()
        print("3. JAVA-SPECIFIC AUTOMATION:")
        print("   - Use Java Access Bridge")
        print("   - Use tools like SikuliX for image-based automation")
        print("   - Use Java Robot class if you can inject code")
        print()
        print("4. ALTERNATIVE APPROACHES:")
        print("   - Check if the application has command-line parameters")
        print("   - Look for configuration files you can modify")
        print("   - Check if there's an API or scripting interface")
        
        # Get window coordinates for coordinate-based automation
        try:
            window_element = automation.driver.find_element_by_xpath("//Window")
            window_rect = window_element.get_attribute("BoundingRectangle")
            if window_rect:
                print(f"\n5. COORDINATE REFERENCE:")
                print(f"   Window bounds: {window_rect}")
                
                # Parse coordinates
                parts = window_rect.replace("Left:", "").replace("Top:", "").replace("Width:", "").replace("Height:", "").split()
                if len(parts) >= 4:
                    left, top, width, height = map(int, parts)
                    print(f"   Estimated menu coordinates:")
                    print(f"   - File menu: ({left + 50}, {top + 35})")
                    print(f"   - Actions menu: ({left + 100}, {top + 35})")
                    print(f"   - Configuration menu: ({left + 180}, {top + 35})")
                    print(f"   - Help menu: ({left + 280}, {top + 35})")
        except Exception as e:
            print(f"Could not get window coordinates: {e}")
        
        print("\n" + "="*60)
        
        # Disconnect
        automation.disconnect()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 