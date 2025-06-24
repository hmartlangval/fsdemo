"""
Manual Automation Helper Functions
"""

import win32gui
import win32con
import win32api
import time
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import json
import os
from pynput import mouse, keyboard


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


class ManualAutomationConfiguration:
    def __init__(self, target_window_title="Brand Test Tool"):
        """
        Initialize the configuration modal.
        
        Args:
            target_window_title: Title of the target application window
        """
        self.target_window_title = target_window_title
        self.target_hwnd = None
        self.is_capturing = False
        self.captured_sequence = []
        self.mouse_listener = None
        self.keyboard_listener = None
        
        self.create_modal()
    
    def create_modal(self):
        """Create the configuration modal window."""
        self.root = tk.Toplevel()
        self.root.title("Manual Automation Configuration")
        self.root.geometry("500x300")
        self.root.resizable(False, False)
        self.root.grab_set()  # Make it modal
        
        # Center the window
        self.root.transient()
        self.root.focus_force()
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Manual Automation Configuration",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Target window info
        target_frame = ttk.LabelFrame(main_frame, text="Target Window", padding="10")
        target_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(target_frame, text=f"Target: {self.target_window_title}").pack(anchor=tk.W)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        # Setup Window button
        self.setup_btn = ttk.Button(
            buttons_frame,
            text="Setup Window",
            command=self.setup_window,
            width=20
        )
        self.setup_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Capture Sequence button
        self.capture_btn = ttk.Button(
            buttons_frame,
            text="Capture Sequence",
            command=self.start_capture_sequence,
            width=20
        )
        self.capture_btn.pack(side=tk.LEFT)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        self.status_text = tk.Text(status_frame, height=8, wrap=tk.WORD)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for status
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.config(yscrollcommand=scrollbar.set)
        
        self.log_status("Configuration window ready")
        
        # Close button
        close_btn = ttk.Button(
            main_frame,
            text="Close",
            command=self.close_modal
        )
        close_btn.pack(pady=(10, 0))
    
    def log_status(self, message):
        """Log a status message."""
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.root.update()
    
    def setup_window(self):
        """Setup the target application window."""
        self.log_status("Setting up target window...")
        
        try:
            # Find target window
            hwnd = win32gui.FindWindow(None, self.target_window_title)
            if not hwnd:
                self.log_status(f"❌ Window not found: '{self.target_window_title}'")
                return
            
            self.target_hwnd = hwnd
            self.log_status(f"✅ Found window: '{self.target_window_title}' (Handle: {hwnd})")
            
            # Bring to focus
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.1)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.1)
            self.log_status("✅ Window brought to focus")
            
            # Resize and position window
            target_left = 56
            target_top = 37
            target_right = 985
            target_bottom = 609
            
            width = target_right - target_left
            height = target_bottom - target_top
            
            win32gui.MoveWindow(hwnd, target_left, target_top, width, height, True)
            time.sleep(0.2)
            
            # Verify positioning
            current_rect = win32gui.GetWindowRect(hwnd)
            self.log_status(f"✅ Window repositioned:")
            self.log_status(f"   Target: Left:{target_left} Top:{target_top} Right:{target_right} Bottom:{target_bottom}")
            self.log_status(f"   Actual: Left:{current_rect[0]} Top:{current_rect[1]} Right:{current_rect[2]} Bottom:{current_rect[3]}")
            
            self.log_status("🎉 Window setup completed!")
            
        except Exception as e:
            self.log_status(f"❌ Error setting up window: {e}")
    
    def start_capture_sequence(self):
        """Start the sequence capture process."""
        if self.is_capturing:
            self.log_status("⚠️ Already capturing - press ESC to stop")
            return
        
        # Show confirmation dialog
        result = messagebox.askyesno(
            "Capture Sequence",
            "This will start capturing mouse clicks and keyboard input.\n\n"
            "Instructions:\n"
            "• Click and type as needed\n"
            "• Press ESC to stop capturing\n"
            "• Target window will be brought to focus\n\n"
            "Proceed with capture?",
            parent=self.root
        )
        
        if not result:
            self.log_status("Capture cancelled by user")
            return
        
        # Ensure target window is focused
        if not self.target_hwnd:
            hwnd = win32gui.FindWindow(None, self.target_window_title)
            if hwnd:
                self.target_hwnd = hwnd
            else:
                self.log_status(f"❌ Target window not found: {self.target_window_title}")
                return
        
        # Bring target window to focus
        try:
            win32gui.ShowWindow(self.target_hwnd, win32con.SW_RESTORE)
            time.sleep(0.1)
            win32gui.SetForegroundWindow(self.target_hwnd)
            time.sleep(0.5)
            self.log_status("✅ Target window focused for capture")
        except Exception as e:
            self.log_status(f"⚠️ Could not focus target window: {e}")
        
        # Start capturing
        self.is_capturing = True
        self.captured_sequence = []
        self.capture_btn.config(text="Capturing... (ESC to stop)", state="disabled")
        self.log_status("🔴 Capture started - press ESC to stop")
        
        # Start listeners
        self.start_listeners()
    
    def start_listeners(self):
        """Start mouse and keyboard listeners."""
        try:
            # Mouse listener (only clicks, not movement)
            self.mouse_listener = mouse.Listener(
                on_click=self.on_mouse_click
            )
            self.mouse_listener.start()
            
            # Keyboard listener
            self.keyboard_listener = keyboard.Listener(
                on_press=self.on_key_press,
                on_release=self.on_key_release
            )
            self.keyboard_listener.start()
            
        except Exception as e:
            self.log_status(f"❌ Error starting listeners: {e}")
            self.stop_capture()
    
    def on_mouse_click(self, x, y, button, pressed):
        """Handle mouse click events."""
        if not self.is_capturing:
            return
        
        if pressed and button == mouse.Button.left:
            self.captured_sequence.append({
                'type': 'click',
                'coordinate': (x, y),
                'timestamp': time.time()
            })
            self.log_status(f"📍 Click captured: ({x}, {y})")
    
    def on_key_press(self, key):
        """Handle key press events."""
        if not self.is_capturing:
            return
        
        # Check for ESC to stop capture
        if key == keyboard.Key.esc:
            self.stop_capture()
            return
        
        # Capture other keys
        try:
            if hasattr(key, 'char') and key.char:
                # Regular character
                self.captured_sequence.append({
                    'type': 'type',
                    'text': key.char,
                    'timestamp': time.time()
                })
                self.log_status(f"⌨️ Key captured: '{key.char}'")
            else:
                # Special key
                key_name = str(key).replace('Key.', '')
                self.captured_sequence.append({
                    'type': 'keys',
                    'key_combination': f"{{{key_name}}}",
                    'timestamp': time.time()
                })
                self.log_status(f"⌨️ Special key captured: {key_name}")
        except Exception as e:
            self.log_status(f"⚠️ Key capture error: {e}")
    
    def on_key_release(self, key):
        """Handle key release events (not used currently)."""
        pass
    
    def stop_capture(self):
        """Stop the capture process."""
        if not self.is_capturing:
            return
        
        self.is_capturing = False
        
        # Stop listeners
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
        
        self.capture_btn.config(text="Capture Sequence", state="normal")
        self.log_status(f"🛑 Capture stopped - {len(self.captured_sequence)} actions captured")
        
        if self.captured_sequence:
            self.save_sequence()
    
    def save_sequence(self):
        """Save the captured sequence."""
        # Ask for sequence name
        sequence_name = simpledialog.askstring(
            "Save Sequence",
            "Enter a name for this sequence:",
            parent=self.root
        )
        
        if not sequence_name:
            self.log_status("Save cancelled - no name provided")
            return
        
        try:
            # Create sequence data
            sequence_data = {
                'name': sequence_name,
                'target_window': self.target_window_title,
                'created': time.strftime("%Y-%m-%d %H:%M:%S"),
                'actions': self.captured_sequence
            }
            
            # Load existing sequences or create new file
            sequences_file = "test_manual_sequences.py"
            sequences = {}
            
            if os.path.exists(sequences_file):
                try:
                    with open(sequences_file, 'r') as f:
                        content = f.read()
                        # Extract sequences dict from file
                        if 'SEQUENCES = ' in content:
                            import ast
                            start = content.find('SEQUENCES = ') + 12
                            end = content.find('\n\n', start)
                            if end == -1:
                                end = len(content)
                            sequences_str = content[start:end]
                            sequences = ast.literal_eval(sequences_str)
                except Exception as e:
                    self.log_status(f"⚠️ Could not load existing sequences: {e}")
                    sequences = {}
            
            # Add new sequence
            sequences[sequence_name] = sequence_data
            
            # Write sequences file
            with open(sequences_file, 'w') as f:
                f.write('"""\nManual Automation Sequences\n"""\n\n')
                f.write('SEQUENCES = ')
                f.write(json.dumps(sequences, indent=2))
                f.write('\n')
            
            self.log_status(f"✅ Sequence '{sequence_name}' saved to {sequences_file}")
            
        except Exception as e:
            self.log_status(f"❌ Error saving sequence: {e}")
    
    def close_modal(self):
        """Close the configuration modal."""
        if self.is_capturing:
            self.stop_capture()
        
        self.root.destroy()
    
    def show(self):
        """Show the configuration modal."""
        self.root.mainloop()
