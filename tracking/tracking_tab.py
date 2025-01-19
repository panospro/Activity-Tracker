import tkinter as tk
from tkinter import ttk
import time
import threading
from collections import defaultdict
from database import setup_database, record_window_activity
from tracking.utils import format_time, load_process_icon, get_window_info

# Global variables
tracking_active = False
window_times = defaultdict(float)
current_windows = {}
session_start_time = None
process_icons = {}

def tracking_thread():
    """Track window activity and update `window_times` and `current_windows` accordingly."""
    global tracking_active, current_windows, window_times
    last_valid_window = None

    while tracking_active:
        try:
            current_info = get_window_info() or last_valid_window
            if current_info:
                last_valid_window = current_info
                window_key = current_info['window_key']
                current_time = time.time()

                # Update elapsed time for the current window
                if window_key in current_windows:
                    elapsed = current_time - current_windows[window_key]
                    window_times[window_key] += elapsed
                    record_window_activity(current_info['window_title'], current_info['process_name'], elapsed)

                # Reset current windows tracking
                current_windows.clear()
                current_windows[window_key] = current_time

            time.sleep(1)
        except Exception as e:
            print(f"Error in tracking thread: {e}")
            if tracking_active:
                threading.Thread(target=tracking_thread, daemon=True).start()

def update_timer(timer_label):
    """Update the timer label with the current session duration."""
    if tracking_active and session_start_time:
        elapsed_time = int(time.time() - session_start_time)
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        timer_label.config(text=f"{hours:02}:{minutes:02}:{seconds:02}")
    timer_label.after(1000, update_timer, timer_label)

def update_tracking_data(tree, frame):
    """Update the treeview with the current tracking data."""
    if not tracking_active:
        return

    # Update window times
    current_time = time.time()
    for window_key, start_time in current_windows.copy().items():
        elapsed = current_time - start_time
        window_times[window_key] += elapsed
        process_name, window_title = window_key.split('|', 1)
        record_window_activity(window_title, process_name, elapsed)
        current_windows[window_key] = current_time

    # Update Treeview
    tree.delete(*tree.get_children())
    process_groups = defaultdict(list)
    for window_key, time_spent in window_times.items():
        process_name, window_title = window_key.split('|', 1)
        process_groups[process_name].append((window_title, time_spent))

    for process_name, windows in process_groups.items():
        total_time = sum(time for _, time in windows)
        icon_image = load_process_icon(process_name, process_icons)
        process_item = tree.insert("", "end", text=f"{process_name} (Total: {format_time(total_time)})", image=icon_image, open=True)

        for window_title, time_spent in sorted(windows, key=lambda x: x[1], reverse=True):
            tree.insert(process_item, "end", text=f"{window_title} ({format_time(time_spent)})")

    frame.after(1000, update_tracking_data, tree, frame)

def toggle_tracking(tree, tracking_button, status_label, timer_label, frame):
    """Toggle the tracking state and update UI accordingly."""
    global tracking_active, session_start_time, window_times, current_windows

    tracking_active = not tracking_active
    if tracking_active:
        session_start_time = time.time()
        threading.Thread(target=tracking_thread, daemon=True).start()
        tracking_button.config(text="⏹ Stop Tracking", bg="#FF4136", activebackground="#FF6F61")
        status_label.config(text="Tracking is ON", fg="#28A745")
        tree.delete(*tree.get_children())
        window_times.clear()
        current_windows.clear()
    else:
        session_start_time = None
        tracking_button.config(text="▶ Start Tracking", bg="#007BFF", activebackground="#66A2FF")
        status_label.config(text="Tracking is OFF", fg="#DC3545")

    update_timer(timer_label)
    update_tracking_data(tree, frame)

def tracking_tab(parent):
    """Create and return the tracking tab frame."""
    global process_icons
    setup_database()

    frame = tk.Frame(parent, bg="#F5F5F5")
    frame.pack(fill="both", expand=True)

    timer_label = tk.Label(frame, text="00:00:00", font=("Helvetica", 36, "bold"), bg="#F5F5F5", fg="#333")
    timer_label.pack(pady=20)

    status_label = tk.Label(frame, text="Tracking is OFF", font=("Helvetica", 14, "italic"), bg="#F5F5F5", fg="#DC3545")
    status_label.pack(pady=10)

    tracking_button = tk.Button(
        frame, text="▶ Start Tracking", font=("Helvetica", 14, "bold"), bg="#007BFF", fg="#FFF",
        padx=20, pady=10, relief="flat", activebackground="#66A2FF", activeforeground="#FFF",
        command=lambda: toggle_tracking(tree, tracking_button, status_label, timer_label, frame)
    )
    tracking_button.pack(pady=20)

    data_frame = tk.Frame(frame, bg="#FFFFFF", relief="groove", bd=2)
    data_frame.pack(fill="both", expand=True, padx=20, pady=20)

    style = ttk.Style()
    style.configure("Treeview", rowheight=50)

    tree = ttk.Treeview(data_frame)
    tree.pack(fill="both", expand=True, padx=5, pady=5)

    process_icons = {}
    return frame
