"""Simple utility to find window handle by title."""
import win32gui
import win32process

def find_window_handle_by_title(target_title: str):
    """Find window handle and process info by window title."""
    result = None
    
    def enum_callback(hwnd, _):
        nonlocal result
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if target_title.lower() in title.lower():
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    result = {
                        'hwnd': hwnd,
                        'pid': pid,
                        'title': title,
                        'class_name': win32gui.GetClassName(hwnd)
                    }
                except Exception:
                    pass
    
    win32gui.EnumWindows(enum_callback, None)
    return result

def list_windows():
    """List all visible windows with their titles."""
    windows = []
    
    def enum_callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title.strip():  # Only include windows with non-empty titles
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    windows.append({
                        'title': title,
                        'pid': pid,
                        'hwnd': hwnd
                    })
                except Exception:
                    pass
    
    win32gui.EnumWindows(enum_callback, None)
    return sorted(windows, key=lambda w: w['title'].lower())

def discover_windows():
    """Print information about all visible windows."""
    print("\n=== Visible Windows ===")
    print("These are the windows you can automate. Use the exact title when running the script.\n")
    
    for window in list_windows():
        print(f"Title: {window['title']}")
        print(f"PID: {window['pid']}")
        print(f"Handle: {window['hwnd']}")
        print()

if __name__ == "__main__":
    discover_windows() 