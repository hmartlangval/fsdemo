# Universal Windows Automation System

A centralized automation framework that **auto-detects** Windows application types and provides **specialized handlers** for different technologies (Java Swing, .NET WPF/WinForms, Win32, etc.).

## 🏗️ Architecture

### Base Class: `BaseWindowAutomation`
- **Common functionality**: Desktop session creation, connection, cleanup
- **Abstract methods**: Must be implemented by specialized handlers
- **Auto-detection**: Analyzes window properties to determine app type

### Specialized Handlers

#### `JavaWindowAutomation`
- **Target**: Java Swing applications (SunAwtFrame)
- **Menu Navigation**: Keyboard shortcuts (Alt+F, Alt+A, etc.)
- **Element Detection**: Handles Java's limited UI Automation exposure
- **Form Filling**: Java-specific input handling

#### `DotNetWindowAutomation` 
- **Target**: .NET WPF and WinForms applications
- **Menu Navigation**: Native UI Automation menu access
- **Element Detection**: Full .NET control tree access
- **Form Filling**: Native .NET input controls

### Universal Entry Point: `UniversalWindowAutomation`
- **Auto-Detection**: Determines app type and creates appropriate handler
- **Unified Interface**: Same methods work across all app types
- **Extensible**: Easy to add more specialized handlers

## 🚀 Usage Examples

### Simple Detection Test
```python
from universal_automation import connect_to_application, cleanup_and_disconnect

# Auto-detect and connect
automation = connect_to_application("My Application")
if automation:
    print(f"Detected type: {automation.app_type}")
    print(f"Handler: {automation.handler.__class__.__name__}")
    cleanup_and_disconnect(automation)
```

### Complete Workflow
```python
from universal_automation import (
    connect_to_application,
    navigate_menu_and_select,
    identify_dialog_type,
    fill_form_inputs,
    cleanup_and_disconnect
)

# Step 1: Connect with auto-detection
automation = connect_to_application("Brand Test Tool")

# Step 2: Navigate menu (works for both Java and .NET)
navigate_menu_and_select(automation, "File", "New")

# Step 3: Identify dialog type
dialog_info = identify_dialog_type(automation)
print(f"Dialog type: {dialog_info['type']}")

# Step 4: Fill form based on what was detected
if dialog_info['type'] == 'multi_input_form':
    fill_form_inputs(automation, ["first input", "second input"])

# Step 5: Cleanup
cleanup_and_disconnect(automation)
```

### Command Line Testing
```bash
# Test detection only
python test_universal_automation.py --title "Brand Test Tool" --detect-only

# Test complete workflow
python test_universal_automation.py --title "Brand Test Tool" --menu "File" --item "New" --form-data "input1" "input2"

# Test .NET application
python test_universal_automation.py --title "Calculator" --menu "View" --item "Scientific"
```

## 🔍 Application Type Detection

The system automatically detects application types based on:

| App Type | Detection Criteria | Handler Used |
|----------|-------------------|--------------|
| **Java** | ClassName contains 'SunAwt' | `JavaWindowAutomation` |
| **.NET WPF** | FrameworkId = 'WPF' | `DotNetWindowAutomation` |
| **.NET WinForms** | FrameworkId = 'WinForm' | `DotNetWindowAutomation` |
| **UWP** | FrameworkId = 'XAML' | `DotNetWindowAutomation` |
| **Win32** | Classic Win32 controls | `JavaWindowAutomation` (fallback) |
| **Unknown** | Fallback case | `JavaWindowAutomation` (keyboard-based) |

## 🎯 Dialog Type Classification

The system identifies dialog types automatically:

- **`multi_input_form`**: 2+ input fields detected
- **`single_input_form`**: 1 input field detected  
- **`button_dialog`**: Only buttons, no input fields
- **`none`**: No dialog appeared
- **`unknown`**: Unrecognized dialog structure

## 🧩 Modular Functions (Legacy Compatibility)

For backward compatibility, these convenience functions are available:

```python
# These work exactly like the old modular functions
automation = connect_to_application(app_title)
navigate_menu_and_select(automation, menu_path, target_item)
dialog_info = identify_dialog_type(automation)
fill_form_inputs(automation, input_data)
cleanup_and_disconnect(automation)
```

## 🔧 Extending the System

### Adding New Application Types

1. **Create new handler class**:
```python
class ElectronWindowAutomation(BaseWindowAutomation):
    def navigate_menu(self, menu_path, target_item):
        # Electron-specific menu navigation
        pass
    
    def identify_dialog_elements(self, wait_timeout=5):
        # Electron-specific dialog detection
        pass
    
    def fill_form_inputs(self, input_data):
        # Electron-specific form filling
        pass
```

2. **Update detection logic** in `BaseWindowAutomation.detect_application_type()`:
```python
elif 'Electron' in class_name or 'Chrome' in class_name:
    return 'electron'
```

3. **Add handler creation** in `UniversalWindowAutomation.connect()`:
```python
elif detected_type == 'electron':
    self.handler = ElectronWindowAutomation(self.app_identifier, self.use_title)
```

### Adding New Dialog Types

1. **Update classification logic** in handler's `_analyze_dialog_elements()`:
```python
elif self._is_confirmation_dialog(input_fields, buttons):
    dialog_info['type'] = 'confirmation_dialog'
```

2. **Add handler function**:
```python
def handle_confirmation_dialog(automation, dialog_info, confirm=True):
    # Handle confirmation dialogs
    pass
```

## 📁 File Structure

```
fsdemo/
├── universal_automation.py          # Main universal system
├── test_universal_automation.py     # Test script
├── windows_automation.py            # Base WinAppDriver wrapper
├── test_deep_ui_discovery.py        # Legacy Java-specific script
└── UNIVERSAL_AUTOMATION_README.md   # This documentation
```

## 🎉 Benefits

- **Single Entry Point**: One system handles all application types
- **Auto-Detection**: No need to specify app type manually
- **Extensible**: Easy to add support for new technologies
- **Backward Compatible**: Existing modular functions still work
- **Type-Specific Optimization**: Each handler optimized for its technology
- **Future-Ready**: Built for adding new dialog types and actions

## 🔮 Future Enhancements

- **Electron/Chrome Apps**: Add handler for web-based desktop apps
- **Qt Applications**: Add handler for Qt-based applications  
- **Custom Controls**: Add support for third-party control libraries
- **Image Recognition**: Fallback to image-based automation
- **AI-Powered Detection**: Use ML to improve dialog classification
- **Recording/Playback**: Record actions and replay them
- **Test Generation**: Auto-generate test scripts from recorded actions

This system provides the foundation for a comprehensive Windows automation solution that can grow with your needs! 