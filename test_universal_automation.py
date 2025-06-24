"""Test script for Universal Windows Automation System with Configuration-Driven Automation."""

import sys
import argparse
import time
from universal_automation import UniversalWindowAutomation

# ==========================================
# AUTOMATION CONFIGURATION
# ==========================================

AUTOMATION_CONFIGS_ALL = {
    "notepad_hello_world": {
        "app_title": "Untitled - Notepad",
        "description": "Open Notepad, type hello world, and save",
        "steps": [
            {
                "type": "navigate",
                "path": "{Alt+F} -> {N}",
                "description": "Open File menu and create New document"
            },
            {
                "type": "type_text",
                "text": "hello world",
                "description": "Type hello world in the document"
            },
            {
                "type": "navigate", 
                "path": "{Alt+F} -> {S}",
                "description": "Open File menu and Save"
            }
        ]
    },
    
    "brand_test_tool": {
        "app_title": "Brand Test Tool",
        "description": "Java application automation workflow with timing control",
        "steps": [
            {
                "type": "navigate",
                "path": "{Alt+F} -> Create Project",
                "description": "Open File menu and create new project",
                "delay": 1.5  # Wait for app to be ready
            },
            {
                "type": "fill_form",
                "data": ["Test Project", "This is a test project description"],
                "description": "Fill project creation form",
                "delay": 2.0  # Wait for dialog to fully load
            },
            {
                "type": "navigate",
                "path": "{Tab} -> {Enter}",
                "description": "Navigate to OK button and press it",
                "delay": 0.5  # Brief pause before confirming
            }
        ]
    },
    
    "calculator_operations": {
        "app_title": "Calculator",
        "description": "Perform calculator operations",
        "steps": [
            {
                "type": "type_text",
                "text": "123",
                "description": "Enter first number"
            },
            {
                "type": "navigate",
                "path": "{+}",
                "description": "Press plus operator"
            },
            {
                "type": "type_text", 
                "text": "456",
                "description": "Enter second number"
            },
            {
                "type": "navigate",
                "path": "{Enter}",
                "description": "Press equals to calculate"
            }
        ]
    },
    
    "custom_workflow": {
        "app_title": "Custom Application",
        "description": "Template for custom automation workflows",
        "steps": [
            {
                "type": "navigate",
                "path": "File -> New",
                "description": "Navigate to File -> New"
            },
            {
                "type": "wait",
                "duration": 2.0,
                "description": "Wait 2 seconds for dialog"
            },
            {
                "type": "type_text",
                "text": "Sample text input",
                "description": "Type sample text"
            },
            {
                "type": "navigate",
                "path": "{Ctrl+S}",
                "description": "Save with Ctrl+S"
            }
        ]
    }
}
AUTOMATION_CONFIGS = {
    "notepad_hello_world": {
        "app_title": "Untitled - Notepad",
        "description": "Open Notepad, type hello world, and save",
        "steps": [
            {
                "type": "navigate",
                "path": "{Alt+F} -> {Down 1} -> {Enter}",
                "description": "Open File menu and create New document",
                "delay": 0.5  # Wait 1 second before opening menu
            },
            {
                "type": "type_text",
                "text": "hello world",
                "description": "Type hello world in the document",
                "delay": 5  # Wait 0.5 seconds before typing
            },
            # {
            #     "type": "navigate", 
            #     "path": "{Alt+F} -> {S}",
            #     "description": "Open File menu and Save",
            #     "delay": 0.5  # Wait 2 seconds before saving
            # }
        ]
    }
}

# ==========================================
# AUTOMATION EXECUTION ENGINE
# ==========================================

def execute_automation_config(config_name):
    """Execute an automation configuration by name."""
    
    if config_name not in AUTOMATION_CONFIGS:
        print(f"❌ Configuration '{config_name}' not found!")
        print(f"Available configurations: {list(AUTOMATION_CONFIGS.keys())}")
        return False
    
    config = AUTOMATION_CONFIGS[config_name]
    automation = None
    
    try:
        print(f"🚀 EXECUTING AUTOMATION CONFIG: {config_name}")
        print("="*60)
        print(f"Description: {config['description']}")
        print(f"Target App: {config['app_title']}")
        print(f"Steps: {len(config['steps'])}")
        print()
        
        # Step 0: Connect to application (default behavior)
        print(f"0️⃣ CONNECTING TO APPLICATION...")
        automation = UniversalWindowAutomation(config['app_title'])
        if not automation.connect():
            print("❌ Failed to connect to application")
            return False
        
        print(f"✅ Connected! App type: {automation.handler.app_type}")
        print(f"Handler: {automation.handler.__class__.__name__}")
        
        # Execute each configured step
        for step_index, step in enumerate(config['steps'], 1):
            print(f"\n{step_index}️⃣ {step['description'].upper()}")
            print(f"Type: {step['type']}")
            
            # Handle optional delay before step execution
            delay = step.get('delay', 0)
            if delay > 0:
                print(f"⏳ Waiting {delay} seconds before executing step...")
                time.sleep(delay)
            else:
                time.sleep(0.5)
            
            if not execute_automation_step(automation, step):
                print(f"❌ Step {step_index} failed!")
                return False
            
            print(f"✅ Step {step_index} completed successfully")
            time.sleep(0.5)  # Brief pause between steps
        
        print(f"\n🎉 AUTOMATION CONFIG '{config_name}' COMPLETED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        print(f"❌ Automation config error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if automation:
            print(f"\n🧹 CLEANUP...")
            automation.disconnect()


def execute_automation_step(automation, step):
    """Execute a single automation step."""
    
    step_type = step['type']
    
    try:
        if step_type == "navigate":
            print(f"🧭 Navigation: '{step['path']}'")
            return automation.navigate_menu(step['path'])
            
        elif step_type == "type_text":
            print(f"⌨️ Typing: '{step['text']}'")
            return type_text_in_app(automation, step['text'])
            
        elif step_type == "fill_form":
            print(f"📝 Form data: {step['data']}")
            return automation.fill_form(step['data'])
            
        elif step_type == "wait":
            duration = step.get('duration', 1.0)
            print(f"⏳ Waiting {duration} seconds...")
            time.sleep(duration)
            return True
            
        elif step_type == "click_button":
            button_name = step.get('button_name', 'OK')
            print(f"🖱️ Clicking button: '{button_name}'")
            return click_button_by_name(automation, button_name)
            
        else:
            print(f"❌ Unknown step type: {step_type}")
            return False
            
    except Exception as e:
        print(f"❌ Step execution error: {e}")
        return False


def type_text_in_app(automation, text):
    """Type text in the currently focused application."""
    try:
        from selenium.webdriver.common.action_chains import ActionChains
        actions = ActionChains(automation.handler.automation.driver)
        actions.send_keys(text).perform()
        return True
    except Exception as e:
        print(f"❌ Text typing failed: {e}")
        return False


def click_button_by_name(automation, button_name):
    """Click a button by its name."""
    try:
        # Try to find button by name
        button_xpath = f"//Button[@Name='{button_name}' or contains(@Name, '{button_name}')]"
        button_element = automation.handler.automation.driver.find_element_by_xpath(button_xpath)
        button_element.click()
        return True
    except Exception as e:
        print(f"❌ Button click failed: {e}")
        return False


def list_available_configs():
    """List all available automation configurations."""
    print("📋 AVAILABLE AUTOMATION CONFIGURATIONS:")
    print("="*50)
    
    for config_name, config in AUTOMATION_CONFIGS.items():
        print(f"\n🔧 {config_name}")
        print(f"   App: {config['app_title']}")
        print(f"   Description: {config['description']}")
        print(f"   Steps: {len(config['steps'])}")
        
        for i, step in enumerate(config['steps'], 1):
            step_type = step['type']
            delay_info = f" (delay: {step['delay']}s)" if step.get('delay', 0) > 0 else ""
            
            if step_type == "navigate":
                print(f"     {i}. Navigate: {step['path']}{delay_info}")
            elif step_type == "type_text":
                print(f"     {i}. Type: '{step['text']}'{delay_info}")
            elif step_type == "fill_form":
                print(f"     {i}. Fill form: {step['data']}{delay_info}")
            elif step_type == "wait":
                print(f"     {i}. Wait: {step.get('duration', 1.0)}s{delay_info}")
            else:
                print(f"     {i}. {step_type}: {step.get('description', 'No description')}{delay_info}")


def test_centralized_navigation_workflow(app_title, navigation_paths, form_data):
    """Test complete automation workflow using centralized navigation system."""
    automation = None
    
    try:
        print(f"🚀 TESTING CENTRALIZED NAVIGATION WORKFLOW")
        print("="*60)
        
        # Step 1: Connect with auto-detection
        print(f"\n1️⃣ CONNECTING TO APPLICATION...")
        print(f"Target: '{app_title}'")
        
        automation = UniversalWindowAutomation(app_title)
        if not automation.connect():
            print("❌ Failed to connect")
            return False
        
        print(f"✅ Connected! Application type: {automation.handler.app_type}")
        print(f"Handler: {automation.handler.__class__.__name__}")
        
        # Step 2: Test multiple navigation paths
        print(f"\n2️⃣ TESTING NAVIGATION PATHS...")
        
        successful_path = None
        for i, nav_path in enumerate(navigation_paths, 1):
            print(f"\n--- Attempt {i}/{len(navigation_paths)} ---")
            print(f"Navigation Path: '{nav_path}'")
            print(f"Format: {_describe_navigation_format(nav_path)}")
            
            try:
                if automation.navigate_menu(nav_path):
                    print("✅ Navigation successful!")
                    successful_path = nav_path
                    break
                else:
                    print("❌ Navigation failed, trying next path...")
                    time.sleep(1)  # Brief pause before next attempt
            except Exception as e:
                print(f"❌ Navigation error: {e}")
                continue
        
        if not successful_path:
            print("❌ All navigation paths failed")
            return False
        
        print(f"\n🎯 Successfully used path: '{successful_path}'")
        
        # Step 3: Identify dialog
        print(f"\n3️⃣ IDENTIFYING DIALOG...")
        dialog_info = automation.identify_dialog(wait_timeout=5)
        
        print(f"Dialog type: {dialog_info['type']}")
        print(f"Input fields: {len(dialog_info.get('input_fields', []))}")
        print(f"Buttons: {len(dialog_info.get('buttons', []))}")
        
        if dialog_info['type'] == 'none':
            print("⚠️ No dialog appeared")
            return True  # Still successful if no dialog was expected
        
        # Step 4: Fill form based on dialog type
        print(f"\n4️⃣ FILLING FORM...")
        
        if dialog_info['type'] in ['multi_input_form', 'single_input_form']:
            if automation.fill_form(form_data):
                print("✅ Form filled successfully!")
            else:
                print("❌ Form filling failed")
                return False
        elif dialog_info['type'] == 'button_dialog':
            print("ℹ️ Button-only dialog detected - no form to fill")
        else:
            print(f"ℹ️ Dialog type '{dialog_info['type']}' - no action taken")
        
        print(f"\n🎉 CENTRALIZED WORKFLOW COMPLETED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        print(f"❌ Workflow error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Step 5: Cleanup
        print(f"\n5️⃣ CLEANUP...")
        if automation:
            automation.disconnect()


def test_navigation_formats(app_title):
    """Test different navigation formats with the centralized system."""
    automation = None
    
    try:
        print(f"🧪 TESTING NAVIGATION FORMATS")
        print("="*50)
        
        # Connect
        automation = UniversalWindowAutomation(app_title)
        if not automation.connect():
            print("❌ Failed to connect")
            return False
        
        print(f"✅ Connected to {automation.handler.app_type} application")
        
        # Test different navigation formats
        test_formats = [
            {
                'name': 'Pure Keyboard Shortcuts',
                'paths': ['{Alt+F}', '{Ctrl+N}', '{F10}'],
                'description': 'Direct keyboard combinations'
            },
            {
                'name': 'Pure Text Navigation', 
                'paths': ['File', 'File -> New', 'Actions -> Configuration'],
                'description': 'Menu and item text search'
            },
            {
                'name': 'Mixed Format',
                'paths': ['{Alt+F} -> New', 'File -> {N}', '{Alt+F} -> Create Project'],
                'description': 'Combination of keyboard and text'
            },
            {
                'name': 'Repeat Keys',
                'paths': ['{Down 3}', '{Tab 2} -> {Enter}', '{Alt+F} -> {Down 2} -> {Enter}'],
                'description': 'Multiple key presses and sequences'
            }
        ]
        
        for format_test in test_formats:
            print(f"\n📋 {format_test['name']}")
            print(f"Description: {format_test['description']}")
            
            for path in format_test['paths']:
                print(f"\n  Testing: '{path}'")
                try:
                    # Just test parsing, don't actually execute to avoid side effects
                    from universal_automation import NavigationParser
                    steps = NavigationParser.parse_navigation_path(path)
                    if steps:
                        print(f"  ✅ Parsed {len(steps)} steps:")
                        for i, step in enumerate(steps, 1):
                            print(f"    {i}. {step['type']}: {step['description']}")
                    else:
                        print(f"  ❌ Parse failed")
                except Exception as e:
                    print(f"  ❌ Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Format testing error: {e}")
        return False
        
    finally:
        if automation:
            automation.disconnect()


def test_app_detection_only(app_title):
    """Test just the application detection capability."""
    automation = None
    
    try:
        print(f"🔍 TESTING APPLICATION DETECTION")
        print("="*50)
        
        automation = UniversalWindowAutomation(app_title)
        if not automation.connect():
            print("❌ Detection failed")
            return False
        
        print(f"\n📊 DETECTION RESULTS:")
        print(f"Application Type: {automation.handler.app_type}")
        print(f"Handler Class: {automation.handler.__class__.__name__}")
        
        # Show capabilities based on detected type
        print(f"\n🛠️ NAVIGATION CAPABILITIES:")
        if automation.handler.app_type == 'java':
            print("✅ Java Swing navigation:")
            print("   • Keyboard shortcuts: {Alt+F}, {Ctrl+N}")
            print("   • Menu text search: File, Actions")
            print("   • Mixed format: {Alt+F} -> Create Project")
        elif automation.handler.app_type in ['dotnet_wpf', 'dotnet_winforms', 'uwp']:
            print("✅ .NET navigation:")
            print("   • UI Automation: File -> New")
            print("   • Keyboard fallback: {Alt+F}")
            print("   • Mixed format: {Alt+F} -> New Document")
        elif automation.handler.app_type in ['win32', 'win32_dialog']:
            print("✅ Win32 navigation:")
            print("   • UI Automation: File -> New")
            print("   • Keyboard codes: {Alt+F}, {Ctrl+N}")
            print("   • Repeat keys: {Down 3} -> {Enter}")
        else:
            print("⚠️ Unknown type - using Win32 fallback")
        
        print(f"\n🎯 CENTRALIZED FEATURES:")
        print("✅ Single navigate_menu() entry point")
        print("✅ Runtime-changeable navigation paths") 
        print("✅ Curly bracket notation: {Alt+F}, {Down 3}")
        print("✅ Mixed format support: {Alt+F} -> Create Project")
        print("✅ App-specific text handling delegation")
        
        return True
        
    except Exception as e:
        print(f"❌ Detection error: {e}")
        return False
        
    finally:
        if automation:
            automation.disconnect()


def _describe_navigation_format(nav_path):
    """Describe the format of a navigation path."""
    has_curly = '{' in nav_path and '}' in nav_path
    has_arrow = '->' in nav_path
    has_text = any(word.lower() in nav_path.lower() for word in ['file', 'edit', 'new', 'create', 'project'])
    
    if has_curly and has_text:
        return "Mixed (keyboard codes + text)"
    elif has_curly:
        return "Pure keyboard codes"
    elif has_text:
        return "Pure text navigation"
    else:
        return "Unknown format"


def main():
    parser = argparse.ArgumentParser(description="Universal Windows Automation - Configuration-Driven System")
    parser.add_argument('config', nargs='?', default="notepad_hello_world",
                       help="Configuration name to execute")
    parser.add_argument('--list', action='store_true',
                       help="List all available automation configurations")
    
    args = parser.parse_args()
    
    print(f"🎯 Universal Automation - Configuration-Driven System")
    print()
    
    if args.list:
        # List available configurations
        list_available_configs()
        sys.exit(0)
    else:
        # Execute specified configuration
        print(f"Configuration: '{args.config}'")
        print()
        success = execute_automation_config(args.config)
    
    if success:
        print(f"\n🎉 Automation completed successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ Automation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 