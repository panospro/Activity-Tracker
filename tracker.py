import time
import sqlite3
import win32gui
import win32process
import psutil
from datetime import datetime

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
def track_active_window():
    current_window = None
    start_time = time.time()

    print("Tracking started. Press Ctrl+C to stop.")
    try:
        while True:
            active_window = get_active_window_title()

            if active_window != current_window:
                # Log time spent on the previous window
                if current_window is not None:
                    end_time = time.time()
                    print(end_time,start_time)
                    time_spent = round(end_time - start_time, 2)
                    log_window_time(current_window, time_spent)
                    print(f"Logged: {current_window} - {time_spent}s")

                # Update to the new window
                current_window = active_window
                start_time = time.time()

            time.sleep(1)  # Check every second
    except KeyboardInterrupt:
        print("\nStopping tracker.")
        if current_window:
            end_time = time.time()
            time_spent = round(end_time - start_time, 2)
            log_window_time(current_window, time_spent)
            print(f"Final Log: {current_window} - {time_spent}s")
