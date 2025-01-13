import time
import sqlite3
import win32gui
import win32process
import psutil
from datetime import datetime
import threading

# TODO: Make it show the picture of process name
def get_active_window_title():
    try:
        # while True:
        #     hwnd = win32gui.GetForegroundWindow()  # Active window handle
        #     window_title = win32gui.GetWindowText(hwnd)  # Active window title
        #     _, pid = win32process.GetWindowThreadProcessId(hwnd)
        #     process_name = psutil.Process(pid).name()
        #     print(process_name)
        #     time.sleep(1) 

        hwnd = win32gui.GetForegroundWindow()  # Active window handle
        window_title = win32gui.GetWindowText(hwnd)  # Active window title
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process_name = psutil.Process(pid).name()

        # Check if the process is File Explorer (explorer.exe) and window title contains folder-related terms
        if process_name.lower() == "explorer.exe":
            return 'Folder'

        if window_title:
            return window_title

        return f"Unknown Window (Process: {process_name})"
    except Exception as e:
        return f"Error retrieving window title: {e}"

def log_window_time(window_title, time_spent):
    with sqlite3.connect('time_tracking.db') as conn:
        conn.execute(
            '''
            INSERT INTO activity_logs (timestamp, window_title, time_spent, category)
            VALUES (?, ?, ?, NULL)
            ''',
            (datetime.now(), window_title, time_spent)
        )

# Calculate the time a window is active
# TODO: Maybe remove the logs and see if the time calculation is ok (because of rounds)

# Global flag to control the tracking thread
tracking_active = False
tracking_thread_instance = None

def track_active_window(start_tracking: bool):
    global tracking_active, tracking_thread_instance

    if start_tracking and not tracking_active:
        def tracking_thread():
            global tracking_active
            current_window = None
            start_time = time.time()

            while tracking_active:  # Continue while the tracking is active
                active_window = get_active_window_title()

                if active_window != current_window:
                    # Log time spent on the previous window
                    if current_window is not None:
                        end_time = time.time()
                        time_spent = round(end_time - start_time, 2)
                        log_window_time(current_window, time_spent)
                        print(f"Logged: {current_window} - {time_spent}s")

                    # Update to the new window
                    current_window = active_window
                    start_time = time.time()

                time.sleep(1)  # Check every second

        tracking_active = True  # Set tracking state to active
        tracking_thread_instance = threading.Thread(target=tracking_thread)
        tracking_thread_instance.start()
        print("Tracking started.")

    elif not start_tracking and tracking_active:
        # Stop tracking
        tracking_active = False  # This will stop the while loop in the thread
        tracking_thread_instance.join()  # Wait for the thread to finish
        print("Tracking stopped.")