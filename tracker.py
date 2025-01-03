import sqlite3
import win32gui
import win32process
import psutil

# **Active Window Tracker**
def get_active_window_title():
    try:
        hwnd = win32gui.GetForegroundWindow()  # Active window handle
        window_title = win32gui.GetWindowText(hwnd)  # Active window title

        if window_title:
            return window_title

        # Retrieve process ID if title is empty
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process_name = psutil.Process(pid).name()
        return f"Unknown Window (Process: {process_name})"
    except Exception as e:
        return f"Error retrieving window title: {e}"
    
# **Log Activity**
def log_activity(window_title):
    with sqlite3.connect('time_tracking.db') as conn:
        conn.execute(
            '''
            INSERT INTO activity_logs (timestamp, window_title, category)
            VALUES (datetime('now'), ?, NULL)
            ''', 
            (window_title,)
        )
