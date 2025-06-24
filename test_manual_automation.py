"""
Manual Automation Script for Window Positioning
"""

import win32gui
import win32con
import win32api
import time
import tkinter as tk
from tkinter import ttk
import threading
from test_manual_helper import ManualAutomationHelper

def find_window_by_title(window_title):
    """Find a window by its title."""
    try:
        hwnd = win32gui.FindWindow(None, window_title)
        if hwnd:
            print(f"✅ Found window: '{window_title}' (Handle: {hwnd})")
            return hwnd
        else:
            print(f"❌ Window not found: '{window_title}'")
            return None
    except Exception as e:
        print(f"❌ Error finding window: {e}")
        return None

def bring_window_to_focus(hwnd):
    """Bring window to foreground and focus."""
    try:
        # Show the window if it's minimized
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(0.1)
        
        # Bring to foreground
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.1)
        
        print(f"✅ Window brought to focus")
        return True
    except Exception as e:
        print(f"❌ Error bringing window to focus: {e}")
        return False

def resize_and_position_window(hwnd, left, top, right, bottom):
    """Resize and reposition window to specified bounding rectangle."""
    try:
        # Calculate width and height from bounding rectangle
        width = right - left
        height = bottom - top
        
        # Move and resize window
        win32gui.MoveWindow(hwnd, left, top, width, height, True)
        time.sleep(0.2)
        
        # Verify the positioning
        current_rect = win32gui.GetWindowRect(hwnd)
        print(f"✅ Window repositioned:")
        print(f"   Target: Left:{left} Top:{top} Right:{right} Bottom:{bottom}")
        print(f"   Actual: Left:{current_rect[0]} Top:{current_rect[1]} Right:{current_rect[2]} Bottom:{current_rect[3]}")
        
        return True
    except Exception as e:
        print(f"❌ Error repositioning window: {e}")
        return False

def setup_application_window(window_title="Brand Test Tool"):
    """Setup application window with positioning."""
    print(f"🎯 Setting up application window: '{window_title}'")
    
    # Target bounding rectangle
    target_left = 56
    target_top = 37
    target_right = 985
    target_bottom = 609
    
    # Step 1: Find window by title
    hwnd = find_window_by_title(window_title)
    if not hwnd:
        return False
    
    # Step 2: Bring to focus
    if not bring_window_to_focus(hwnd):
        return False
    
    # Step 3: Resize and reposition
    if not resize_and_position_window(hwnd, target_left, target_top, target_right, target_bottom):
        return False
    
    print(f"🎉 Application window setup completed!")
    return True

class AutomationToolbar:
    def __init__(self):
        self.root = tk.Tk()
        self.helper = None  # Will be initialized after window setup
        self.target_window_title = "Brand Test Tool"
        self.setup_window()
        self.create_buttons()
        self.initialize_helper()
    
    def initialize_helper(self):
        """Initialize the automation helper."""
        try:
            self.helper = ManualAutomationHelper(window_title=self.target_window_title)
            print(f"✅ Automation helper initialized for: {self.target_window_title}")
        except Exception as e:
            print(f"⚠️ Could not initialize automation helper: {e}")
            print("   Helper will be initialized when needed")
            self.helper = None
    
    def get_helper(self):
        """Get or create automation helper."""
        if self.helper is None:
            try:
                self.helper = ManualAutomationHelper(window_title=self.target_window_title)
                print(f"✅ Automation helper created for: {self.target_window_title}")
            except Exception as e:
                print(f"❌ Failed to create automation helper: {e}")
                return None
        return self.helper
    
    def setup_window(self):
        """Setup the toolbar window properties."""
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Toolbar dimensions
        toolbar_height = 80
        toolbar_width = screen_width
        
        # Position at bottom of screen
        x_position = -10
        y_position = screen_height - toolbar_height - 80
        
        # Configure window
        self.root.title("Manual Automation Toolbar")
        self.root.geometry(f"{toolbar_width}x{toolbar_height}+{x_position}+{y_position}")
        
        # Window properties
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)  # Keep on top
        self.root.configure(bg='#f0f0f0')
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_buttons(self):
        """Create automation control buttons."""
        
        # Button 1: Setup Application Window
        self.setup_btn = ttk.Button(
            self.main_frame,
            text="Setup Application Window",
            command=self.on_setup_window_clicked,
            width=25
        )
        self.setup_btn.pack(side=tk.LEFT, padx=5, pady=10)
        
        # Status label
        self.status_label = tk.Label(
            self.main_frame,
            text="Ready",
            bg='#f0f0f0',
            fg='green',
            font=('Arial', 10)
        )
        self.status_label.pack(side=tk.RIGHT, padx=10, pady=10)
    
    def on_setup_window_clicked(self):
        """Handle setup window button click."""
        self.status_label.config(text="Setting up window...", fg='orange')
        self.root.update()
        
        # Run setup in separate thread to avoid blocking GUI
        thread = threading.Thread(target=self.run_setup)
        thread.daemon = True
        thread.start()
    
    def run_setup(self):
        """Run the setup operation."""
        try:
            success = setup_application_window(self.target_window_title)
            
            # Re-initialize helper after window setup
            if success:
                self.initialize_helper()
            
            # Update status on main thread
            if success:
                self.root.after(0, lambda: self.status_label.config(text="Setup completed ✅", fg='green'))
            else:
                self.root.after(0, lambda: self.status_label.config(text="Setup failed ❌", fg='red'))
        except Exception as e:
            print(f"Error in setup: {e}")
            self.root.after(0, lambda: self.status_label.config(text="Setup error ❌", fg='red'))
    
    def run(self):
        """Start the toolbar application."""
        print("🚀 Starting Manual Automation Toolbar...")
        self.root.mainloop()

def main():
    """Main function."""
    # Create and run the toolbar
    toolbar = AutomationToolbar()
    toolbar.run()

if __name__ == "__main__":
    main()
