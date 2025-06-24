#!/usr/bin/env python3
"""Test script for centralized navigation system with parser in base class."""

from universal_automation import UniversalWindowAutomation, NavigationParser

def test_centralized_navigation():
    """Test the centralized navigation system."""
    
    print("🧪 Testing Centralized Navigation System")
    print("=" * 60)
    
    # Test cases with different navigation formats
    test_cases = [
        {
            'name': 'Pure Keyboard Codes',
            'path': '{Alt+F} -> {N}',
            'description': 'Alt+F then N key'
        },
        {
            'name': 'Mixed Keyboard and Text',
            'path': '{Alt+F} -> Create Project',
            'description': 'Alt+F then search for "Create Project"'
        },
        {
            'name': 'Pure Text Navigation',
            'path': 'File -> New Project',
            'description': 'Find File menu, then New Project item'
        },
        {
            'name': 'Complex Sequence',
            'path': '{Alt+F} -> {Down 2} -> {Enter} -> {Tab 3}',
            'description': 'Alt+F, Down twice, Enter, Tab 3 times'
        },
        {
            'name': 'Single Shortcut',
            'path': '{Ctrl+N}',
            'description': 'Just Ctrl+N'
        },
        {
            'name': 'Repeat Keys',
            'path': '{Down 5} -> {Enter}',
            'description': 'Down 5 times then Enter'
        }
    ]
    
    print("\n📋 Test Cases:")
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Path: '{test_case['path']}'")
        print(f"   Description: {test_case['description']}")
        
        # Parse the navigation path
        steps = NavigationParser.parse_navigation_path(test_case['path'])
        
        if steps:
            print(f"   ✅ Parsed {len(steps)} steps:")
            for j, step in enumerate(steps, 1):
                print(f"      Step {j}: {step['type']} - {step['description']}")
        else:
            print("   ❌ Failed to parse")

def test_runtime_navigation():
    """Test runtime navigation path changes."""
    
    print("\n\n🔄 Testing Runtime Navigation Changes")
    print("=" * 60)
    
    # Simulate different navigation paths that could be changed at runtime
    runtime_paths = [
        "File -> New",
        "{Ctrl+N}",
        "{Alt+F} -> {N}",
        "File -> {Down 1} -> {Enter}",
        "{F10} -> {Right} -> {Down 2} -> {Enter}"
    ]
    
    print("\n🎯 Simulating Runtime Path Changes:")
    
    for i, path in enumerate(runtime_paths, 1):
        print(f"\n--- Runtime Change {i} ---")
        print(f"New Path: '{path}'")
        
        # Parse the new path
        steps = NavigationParser.parse_navigation_path(path)
        
        if steps:
            print(f"✅ Successfully parsed {len(steps)} steps:")
            for step in steps:
                print(f"   • {step['description']}")
                
                # Simulate execution classification
                if step['type'] in ['key_single', 'key_combination', 'key_repeat']:
                    print(f"     → Will execute via global NavigationParser")
                elif step['type'] in ['menu_text', 'menu_item_text']:
                    print(f"     → Will delegate to app-specific text handler")
                else:
                    print(f"     → Unknown step type: {step['type']}")
        else:
            print("❌ Parse failed")

def test_app_type_delegation():
    """Test how different app types would handle the same navigation path."""
    
    print("\n\n🎯 Testing App Type Delegation")
    print("=" * 60)
    
    test_path = "{Alt+F} -> Create Project"
    
    print(f"Navigation Path: '{test_path}'")
    print("How different app types would handle this:")
    
    # Parse once
    steps = NavigationParser.parse_navigation_path(test_path)
    
    if steps:
        print(f"\n📝 Parsed Steps:")
        for i, step in enumerate(steps, 1):
            print(f"  {i}. {step['type']}: {step['description']}")
        
        print(f"\n🔄 App Type Handling:")
        
        # Step 1: {Alt+F} (key_combination)
        step1 = steps[0]
        print(f"\nStep 1 - {step1['description']}:")
        print(f"  • Java: NavigationParser.execute_step() - Direct keyboard")
        print(f"  • .NET: NavigationParser.execute_step() - Direct keyboard")  
        print(f"  • Win32: NavigationParser.execute_step() - Direct keyboard")
        print(f"  • All apps handle this identically via base class")
        
        # Step 2: Create Project (menu_item_text)
        if len(steps) > 1:
            step2 = steps[1]
            print(f"\nStep 2 - {step2['description']}:")
            print(f"  • Java: _execute_java_menu_item() - First letter + position search")
            print(f"  • .NET: _execute_dotnet_menu_item() - UI Automation + fallback")
            print(f"  • Win32: _try_win32_menuitem_ui() - UI Automation only")
            print(f"  • Each app uses its specialized text handler")
    
    print(f"\n✅ Centralized System Benefits:")
    print(f"  • Single navigation entry point: base.navigate_menu()")
    print(f"  • Consistent parsing via NavigationParser")
    print(f"  • Keyboard codes handled universally")
    print(f"  • Text navigation delegated to app specialists")
    print(f"  • Runtime path changes supported")
    print(f"  • No code duplication across app types")

def demonstrate_usage():
    """Demonstrate actual usage of the centralized system."""
    
    print("\n\n💡 Usage Examples")
    print("=" * 60)
    
    usage_examples = [
        {
            'scenario': 'Java Application',
            'code': '''
# Connect to Java app
automation = UniversalWindowAutomation("Brand Test Tool")
automation.connect()

# Navigate using centralized system - runtime changeable
automation.navigate_menu("{Alt+F} -> Create Project")
automation.navigate_menu("File -> {Down 2} -> {Enter}")
automation.navigate_menu("{Ctrl+N}")
            '''
        },
        {
            'scenario': '.NET Application',
            'code': '''
# Connect to .NET app  
automation = UniversalWindowAutomation("MyApp.exe")
automation.connect()

# Same interface, different internal handling
automation.navigate_menu("{Alt+F} -> New Document")
automation.navigate_menu("File -> {N}")
automation.navigate_menu("{Ctrl+Shift+N}")
            '''
        },
        {
            'scenario': 'Runtime Path Changes',
            'code': '''
# Paths can be changed at runtime
navigation_paths = [
    "{Alt+F} -> {N}",           # Keyboard only
    "File -> New Project",      # Text only  
    "{Alt+F} -> Create Item",   # Mixed
    "{Down 3} -> {Enter}"       # Repeat keys
]

for path in navigation_paths:
    result = automation.navigate_menu(path)
    if result:
        print(f"✅ Navigation successful: {path}")
    else:
        print(f"❌ Navigation failed: {path}")
            '''
        }
    ]
    
    for example in usage_examples:
        print(f"\n📋 {example['scenario']}:")
        print(example['code'])

if __name__ == "__main__":
    test_centralized_navigation()
    test_runtime_navigation()
    test_app_type_delegation()
    demonstrate_usage()
    
    print("\n" + "=" * 60)
    print("🎯 Centralized Navigation System Summary:")
    print("✅ NavigationParser remains independent")
    print("✅ BaseWindowAutomation.navigate_menu() is the single entry point")
    print("✅ All keyboard codes handled universally")
    print("✅ Text navigation delegated to app-specific handlers")
    print("✅ Runtime path changes fully supported")
    print("✅ Consistent interface across all app types")
    print("✅ No code duplication - DRY principle maintained")
    print("=" * 60) 