"""Test script for Universal Windows Automation System."""

import sys
import argparse
from universal_automation import (
    connect_to_application,
    navigate_menu_and_select, 
    identify_dialog_type,
    fill_form_inputs,
    cleanup_and_disconnect
)


def test_complete_workflow(app_title, menu_path, menu_item, form_data):
    """Test complete automation workflow with auto-detection."""
    automation = None
    
    try:
        print(f"🚀 TESTING UNIVERSAL AUTOMATION WORKFLOW")
        print("="*60)
        
        # Step 1: Connect with auto-detection
        print(f"\n1️⃣ CONNECTING...")
        automation = connect_to_application(app_title)
        if not automation:
            print("❌ Failed to connect")
            return False
        
        print(f"✅ Connected! Application type: {automation.app_type}")
        
        # Step 2: Navigate menu
        print(f"\n2️⃣ NAVIGATING MENU...")
        print(f"Menu: {menu_path} → {menu_item}")
        
        if not navigate_menu_and_select(automation, menu_path, menu_item):
            print("❌ Menu navigation failed")
            return False
        
        print("✅ Menu navigation successful!")
        
        # Step 3: Identify dialog
        print(f"\n3️⃣ IDENTIFYING DIALOG...")
        dialog_info = identify_dialog_type(automation, wait_timeout=5)
        
        print(f"Dialog type: {dialog_info['type']}")
        print(f"Input fields: {len(dialog_info.get('input_fields', []))}")
        print(f"Buttons: {len(dialog_info.get('buttons', []))}")
        
        if dialog_info['type'] == 'none':
            print("⚠️ No dialog appeared")
            return True  # Still successful if no dialog was expected
        
        # Step 4: Fill form based on dialog type
        print(f"\n4️⃣ FILLING FORM...")
        
        if dialog_info['type'] in ['multi_input_form', 'single_input_form']:
            if fill_form_inputs(automation, form_data):
                print("✅ Form filled successfully!")
            else:
                print("❌ Form filling failed")
                return False
        elif dialog_info['type'] == 'button_dialog':
            print("ℹ️ Button-only dialog detected - no form to fill")
        else:
            print(f"ℹ️ Dialog type '{dialog_info['type']}' - no action taken")
        
        print(f"\n🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
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
            cleanup_and_disconnect(automation)


def test_app_detection_only(app_title):
    """Test just the application detection capability."""
    automation = None
    
    try:
        print(f"🔍 TESTING APPLICATION DETECTION")
        print("="*50)
        
        automation = connect_to_application(app_title)
        if not automation:
            print("❌ Detection failed")
            return False
        
        print(f"\n📊 DETECTION RESULTS:")
        print(f"Application Type: {automation.app_type}")
        print(f"Handler Class: {automation.handler.__class__.__name__}")
        print(f"Window Info: {automation.handler.window_info}")
        
        # Show capabilities based on detected type
        print(f"\n🛠️ AVAILABLE CAPABILITIES:")
        if automation.app_type == 'java':
            print("✅ Java Swing menu navigation (keyboard-based)")
            print("✅ Java dialog element identification")
            print("✅ Java form filling")
        elif automation.app_type in ['dotnet_wpf', 'dotnet_winforms', 'uwp']:
            print("✅ .NET menu navigation (UI Automation)")
            print("✅ .NET dialog element identification")
            print("✅ .NET form filling")
        elif automation.app_type in ['win32', 'win32_dialog']:
            print("✅ Win32 menu navigation (UI Automation + keyboard fallback)")
            print("✅ Win32 dialog element identification")
            print("✅ Win32 form filling")
        else:
            print("⚠️ Unknown type - using Win32 fallback")
        
        return True
        
    except Exception as e:
        print(f"❌ Detection error: {e}")
        return False
        
    finally:
        if automation:
            cleanup_and_disconnect(automation)


def main():
    parser = argparse.ArgumentParser(description="Universal Windows Automation Test")
    parser.add_argument('--title', default="Brand Test Tool", 
                       help="Window title to connect to")
    parser.add_argument('--menu', default="File", 
                       help="Menu to navigate (e.g., File, Edit, Actions)")
    parser.add_argument('--item', default="New", 
                       help="Menu item to select (e.g., New, Open, Save)")
    parser.add_argument('--detect-only', action='store_true',
                       help="Only test application detection")
    parser.add_argument('--form-data', nargs='+', default=["first input", "second input"],
                       help="Data to fill in form fields")
    
    args = parser.parse_args()
    
    if args.detect_only:
        # Test detection only
        success = test_app_detection_only(args.title)
    else:
        # Test complete workflow
        success = test_complete_workflow(
            app_title=args.title,
            menu_path=args.menu,
            menu_item=args.item,
            form_data=args.form_data
        )
    
    if success:
        print(f"\n🎉 Test completed successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ Test failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 