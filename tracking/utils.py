import psutil
import win32gui
import win32process
import os
from tkinter import PhotoImage
from utils import download_process_icon

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

def load_process_icon(process_name, process_icons):
    """Retrieve or download the process icon for the given process name."""
    if process_name not in process_icons:
        icon_path = download_process_icon(process_name)
        if icon_path and os.path.exists(icon_path):
            try:
                # pil_image = Image.open(icon_path).resize((30, 30), Image.Resampling.LANCZOS)
                process_icons[process_name] = PhotoImage(file=icon_path)
            except Exception as e:
                print(f"Failed to load icon for {process_name}: {e}")
    return process_icons.get(process_name)