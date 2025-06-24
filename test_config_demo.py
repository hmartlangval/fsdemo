"""
Demo script for Manual Automation Configuration
"""

import tkinter as tk
from test_manual_helper import ManualAutomationConfiguration

def main():
    """Demo the configuration modal."""
    # Create a root window (will be hidden)
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    
    try:
        # Create and show configuration modal
        config = ManualAutomationConfiguration(target_window_title="Brand Test Tool")
        config.show()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        root.destroy()

if __name__ == "__main__":
    main() 