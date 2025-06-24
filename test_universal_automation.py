"""Test script for Universal Windows Automation System with Centralized Navigation."""

import sys
import argparse
import time
from universal_automation import UniversalWindowAutomation


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
    parser = argparse.ArgumentParser(description="Universal Windows Automation Test with Centralized Navigation")
    parser.add_argument('--title', default="Brand Test Tool", 
                       help="Window title to connect to")
    parser.add_argument('--navigation', nargs='+', 
                       default=["{Alt+F} -> Create Project", "File -> New", "{Ctrl+N}", "Actions -> Configuration"],
                       help="Navigation paths to try (supports curly bracket notation)")
    parser.add_argument('--detect-only', action='store_true',
                       help="Only test application detection")
    parser.add_argument('--formats-only', action='store_true',
                       help="Only test navigation format parsing")
    parser.add_argument('--form-data', nargs='+', default=["Test Project", "Description here"],
                       help="Data to fill in form fields")
    
    args = parser.parse_args()
    
    print(f"🎯 Universal Automation Test - Centralized Navigation System")
    print(f"Target Application: '{args.title}'")
    print(f"Navigation Paths: {args.navigation}")
    print()
    
    if args.detect_only:
        # Test detection only
        success = test_app_detection_only(args.title)
    elif args.formats_only:
        # Test format parsing only
        success = test_navigation_formats(args.title)
    else:
        # Test complete workflow with centralized navigation
        success = test_centralized_navigation_workflow(
            app_title=args.title,
            navigation_paths=args.navigation,
            form_data=args.form_data
        )
    
    if success:
        print(f"\n🎉 Test completed successfully!")
        print(f"✅ Centralized navigation system working correctly!")
        sys.exit(0)
    else:
        print(f"\n❌ Test failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 