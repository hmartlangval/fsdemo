"""
Manual Automation Toolbar
"""

import tkinter as tk
from tkinter import ttk
import threading
from test_manual_helper import ManualAutomationHelper, ManualAutomationConfiguration

class AutomationToolbar:
    def __init__(self):
        self.root = tk.Tk()
        self.helper = None
        self.target_window_title = "Brand Test Tool"
        self.setup_toolbar_window()
        self.create_buttons()
        self.initialize_helper()
    
    def setup_toolbar_window(self):
        """Setup the toolbar window."""
        self.root.title("Manual Automation Toolbar")
        self.root.geometry("400x80")
        self.root.resizable(False, False)
        
        # Position at bottom of screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = -10
        y = screen_height - 160
        self.root.geometry(f"400x80+{x}+{y}")
        
        # Keep on top
        self.root.attributes('-topmost', True)
        
        # Main frame
        self.main_frame = tk.Frame(self.root, bg='#f0f0f0')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
    
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
    
    def create_buttons(self):
        """Create automation control buttons."""
        
        # Configure button
        self.configure_btn = ttk.Button(
            self.main_frame,
            text="Configure",
            command=self.on_configure_clicked,
            width=15
        )
        self.configure_btn.pack(side=tk.LEFT, padx=5, pady=10)
        
        # Status label
        self.status_label = tk.Label(
            self.main_frame,
            text="Ready",
            bg='#f0f0f0',
            fg='green',
            font=('Arial', 10)
        )
        self.status_label.pack(side=tk.RIGHT, padx=10, pady=10)
    
    def on_configure_clicked(self):
        """Handle configure button click."""
        try:
            self.status_label.config(text="Opening configuration...", fg='orange')
            self.root.update()
            
            # Create and show configuration modal
            config = ManualAutomationConfiguration(target_window_title=self.target_window_title)
            config.show()
            
            # Update status after configuration window closes
            self.status_label.config(text="Ready", fg='green')
            
        except Exception as e:
            print(f"Error opening configuration: {e}")
            self.status_label.config(text="Configuration error ❌", fg='red')
    
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
