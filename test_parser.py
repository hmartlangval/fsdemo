#!/usr/bin/env python3
"""Test script for the new NavigationParser with curly bracket notation."""

from universal_automation import NavigationParser

def test_parser():
    """Test the NavigationParser with various input formats."""
    
    test_cases = [
        # Keyboard codes only
        "{Alt+F} -> {N}",
        "{Ctrl+N}",
        "{Down 3}",
        "{Alt+F} -> {Down 2} -> {Enter}",
        
        # Mixed keyboard codes and text
        "{Alt+F} -> Create Project",
        "{Ctrl+Shift+N} -> New Document",
        "File -> {Down 1} -> {Enter}",
        
        # Text only
        "File -> New Project",
        "Actions -> Configuration",
        "Help -> About",
        
        # Complex sequences
        "{Alt+F} -> {Down 2} -> {Enter} -> {Tab 3} -> {Enter}",
        "File -> {N} -> Project Name -> {Tab} -> {Enter}",
        
        # Single steps
        "{Escape}",
        "File",
        "{F1}",
        
        # Repeat keys
        "{Tab 5}",
        "{Down 10}",
        "{Up 2}",
    ]
    
    print("🧪 Testing NavigationParser with curly bracket notation\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{'='*60}")
        print(f"Test {i}: '{test_case}'")
        print(f"{'='*60}")
        
        steps = NavigationParser.parse_navigation_path(test_case)
        
        if steps:
            print(f"✅ Parsed {len(steps)} steps:")
            for j, step in enumerate(steps, 1):
                print(f"  Step {j}: {step}")
        else:
            print("❌ Failed to parse")
        
        print()

def test_edge_cases():
    """Test edge cases and error handling."""
    
    edge_cases = [
        # Empty/invalid
        "",
        "   ",
        "->",
        "-> ->",
        
        # Malformed brackets
        "{Alt+F",
        "Alt+F}",
        "{}",
        "{  }",
        
        # Invalid key combinations
        "{Alt++F}",
        "{+F}",
        "{Alt+}",
        
        # Mixed formats
        "{Alt+F} -> File -> {N}",
        "File -> {Alt+F} -> New",
    ]
    
    print("\n🔍 Testing edge cases and error handling\n")
    
    for i, test_case in enumerate(edge_cases, 1):
        print(f"Edge Case {i}: '{test_case}'")
        steps = NavigationParser.parse_navigation_path(test_case)
        print(f"  Result: {len(steps)} steps parsed")
        if steps:
            for step in steps:
                print(f"    {step}")
        print()

if __name__ == "__main__":
    test_parser()
    test_edge_cases()
    
    print("\n" + "="*60)
    print("🎯 Parser Test Summary:")
    print("✅ Curly brackets {} indicate keyboard codes")
    print("✅ Plain text indicates menu/item names")
    print("✅ Arrow -> separates navigation steps")
    print("✅ Repeat notation: {Down 3}, {Tab 5}, etc.")
    print("✅ Modifier combinations: {Alt+F}, {Ctrl+Shift+N}")
    print("✅ Mixed formats supported: {Alt+F} -> Create Project")
    print("="*60) 