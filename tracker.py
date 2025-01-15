import time
import win32gui
import win32process
import psutil
import threading
from database import log_window_time

# Get the active window title and the process name
def get_active_window_title():
    try:
        hwnd = win32gui.GetForegroundWindow()  # Active window handle
        window_title = win32gui.GetWindowText(hwnd)  # Active window title
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process_name = psutil.Process(pid).name()

        # Check if the process is File Explorer (explorer.exe) and window title contains folder-related terms
        if process_name.lower() == "explorer.exe":
            return 'Folder', process_name

        if window_title:
            return window_title, process_name

        return f"Unknown Window", process_name
    except Exception as e:
# TODO: Maybe remove the logs and see if the time calculation is ok (because of rounds)
        return f"Error retrieving window title: {e}", "Unknown Process"

# Global flag to control the tracking thread
tracking_active = False
tracking_thread_instance = None

# Start or stop the tracking process
def track_active_window(start_tracking: bool):
    global tracking_active, tracking_thread_instance

    if start_tracking and not tracking_active:
        def tracking_thread():
            global tracking_active
            current_window = None
            current_process = None
            start_time = time.time()

            while tracking_active:  # Continue while the tracking is active
                active_window, process_name = get_active_window_title()

                if active_window != current_window or process_name != current_process:
                    # Log time spent on the previous window
                    if current_window is not None:
                        end_time = time.time()
                        time_spent = round(end_time - start_time, 2)
                        log_window_time(current_window, current_process, time_spent)
                        print(f"Logged: {current_window} ({current_process}) - {time_spent}s")

                    # Update to the new window and process
                    current_window = active_window
                    current_process = process_name
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
