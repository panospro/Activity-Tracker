import psutil
import win32gui
import win32process

def get_window_info():
    """
    Validate the current foreground window and retrieve its information.
    Returns a dictionary with window title, process name, and window key, or None if invalid.
    """
    try:
        hwnd = win32gui.GetForegroundWindow()
        
        # Validate hwnd
        if not hwnd or hwnd == 0 or not win32gui.IsWindowVisible(hwnd):
            return None

        # Get window title
        title = win32gui.GetWindowText(hwnd)
        if not title:
            return None

        # Get process ID
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if pid <= 0:
            return None

        # Get process name
        try:
            process = psutil.Process(pid)
            process_name = process.name()
            if not process_name:
                return None
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None

        # Return consolidated window info
        return {
            'window_title': title,
            'process_name': process_name,
            'window_key': f"{process_name}|{title}"
        }

    except Exception as e:
        print(f"Error retrieving window info: {e}")
        return None

def format_time(seconds):
    """Convert seconds to human readable time format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"
