"""
Manual Automation Helper Functions
"""

import win32gui
import win32con
import win32api
import time


class ManualAutomationHelper:
    def __init__(self, window_handle=None, window_title=None):
        """
        Initialize the helper with window information.
        
        Args:
            window_handle: Direct window handle (HWND)
            window_title: Window title to find the handle
        """
        if window_handle:
            self.hwnd = window_handle
        elif window_title:
            self.hwnd = win32gui.FindWindow(None, window_title)
            if not self.hwnd:
                raise ValueError(f"Window not found: '{window_title}'")
        else:
            raise ValueError("Either window_handle or window_title must be provided")
        
        self.window_title = window_title or self._get_window_title()
    
    def _get_window_title(self):
        """Get window title from handle."""
        try:
            return win32gui.GetWindowText(self.hwnd)
        except:
            return "Unknown"
    
    def _bring_to_focus(self):
        """Bring the target window to focus."""
        try:
            # Show window if minimized
            win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
            time.sleep(0.1)
            
            # Bring to foreground
            win32gui.SetForegroundWindow(self.hwnd)
            time.sleep(0.1)
            
            return True
        except Exception as e:
            print(f"Warning: Could not bring window to focus: {e}")
            return False
    
    def type(self, text):
        """
        Type text into the focused window.
        
        Args:
            text: Text string to type
            
        Returns:
            bool: Success status
        """
        try:
            # Bring window to focus
            self._bring_to_focus()
            
            # Type each character
            for char in text:
                # Get virtual key code for character
                vk_code = win32api.VkKeyScan(char)
                if vk_code == -1:
                    # Character not available, skip
                    continue
                
                # Extract key code and shift state
                key_code = vk_code & 0xFF
                shift_state = (vk_code >> 8) & 0xFF
                
                # Press shift if needed
                if shift_state & 1:
                    win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
                
                # Press and release the key
                win32api.keybd_event(key_code, 0, 0, 0)
                win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)
                
                # Release shift if pressed
                if shift_state & 1:
                    win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
                
                time.sleep(0.01)  # Small delay between keystrokes
            
            return True
            
        except Exception as e:
            print(f"Error typing text: {e}")
            return False
    
    def click(self, coordinate):
        """
        Click at the specified coordinate.
        
        Args:
            coordinate: Tuple (x, y) of screen coordinates
            
        Returns:
            bool: Success status
        """
        try:
            # Bring window to focus
            self._bring_to_focus()
            
            x, y = coordinate
            
            # Move cursor to position
            win32api.SetCursorPos((x, y))
            time.sleep(0.1)
            
            # Perform left click
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
            
            return True
            
        except Exception as e:
            print(f"Error clicking at {coordinate}: {e}")
            return False
    
    def keys(self, key_combination):
        """
        Send key combination with modifiers.
        
        Args:
            key_combination: String with modifiers in curly braces
                           Examples: "{Ctrl+F}", "{Enter}", "{Alt+Tab}", "text"
                           
        Returns:
            bool: Success status
        """
        try:
            # Bring window to focus
            self._bring_to_focus()
            
            # Parse key combination
            if key_combination.startswith('{') and key_combination.endswith('}'):
                # Special key combination
                keys_str = key_combination[1:-1]  # Remove braces
                
                # Parse modifiers and key
                modifiers = []
                main_key = keys_str
                
                if '+' in keys_str:
                    parts = keys_str.split('+')
                    modifiers = [part.strip() for part in parts[:-1]]
                    main_key = parts[-1].strip()
                
                # Press modifiers
                modifier_codes = []
                for modifier in modifiers:
                    if modifier.lower() == 'ctrl':
                        modifier_codes.append(win32con.VK_CONTROL)
                        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                    elif modifier.lower() == 'alt':
                        modifier_codes.append(win32con.VK_MENU)
                        win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
                    elif modifier.lower() == 'shift':
                        modifier_codes.append(win32con.VK_SHIFT)
                        win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
                    elif modifier.lower() == 'win':
                        modifier_codes.append(win32con.VK_LWIN)
                        win32api.keybd_event(win32con.VK_LWIN, 0, 0, 0)
                
                time.sleep(0.05)
                
                # Press main key
                main_vk = self._get_virtual_key_code(main_key)
                if main_vk:
                    win32api.keybd_event(main_vk, 0, 0, 0)
                    win32api.keybd_event(main_vk, 0, win32con.KEYEVENTF_KEYUP, 0)
                
                time.sleep(0.05)
                
                # Release modifiers in reverse order
                for modifier_code in reversed(modifier_codes):
                    win32api.keybd_event(modifier_code, 0, win32con.KEYEVENTF_KEYUP, 0)
                
            else:
                # Regular text, use type function
                return self.type(key_combination)
            
            return True
            
        except Exception as e:
            print(f"Error sending keys '{key_combination}': {e}")
            return False
    
    def _get_virtual_key_code(self, key_name):
        """Get virtual key code for special keys."""
        special_keys = {
            'enter': win32con.VK_RETURN,
            'tab': win32con.VK_TAB,
            'space': win32con.VK_SPACE,
            'backspace': win32con.VK_BACK,
            'delete': win32con.VK_DELETE,
            'escape': win32con.VK_ESCAPE,
            'esc': win32con.VK_ESCAPE,
            'home': win32con.VK_HOME,
            'end': win32con.VK_END,
            'pageup': win32con.VK_PRIOR,
            'pagedown': win32con.VK_NEXT,
            'up': win32con.VK_UP,
            'down': win32con.VK_DOWN,
            'left': win32con.VK_LEFT,
            'right': win32con.VK_RIGHT,
            'f1': win32con.VK_F1,
            'f2': win32con.VK_F2,
            'f3': win32con.VK_F3,
            'f4': win32con.VK_F4,
            'f5': win32con.VK_F5,
            'f6': win32con.VK_F6,
            'f7': win32con.VK_F7,
            'f8': win32con.VK_F8,
            'f9': win32con.VK_F9,
            'f10': win32con.VK_F10,
            'f11': win32con.VK_F11,
            'f12': win32con.VK_F12,
        }
        
        key_lower = key_name.lower()
        if key_lower in special_keys:
            return special_keys[key_lower]
        
        # For single characters, try VkKeyScan
        if len(key_name) == 1:
            vk_code = win32api.VkKeyScan(key_name)
            if vk_code != -1:
                return vk_code & 0xFF
        
        return None
