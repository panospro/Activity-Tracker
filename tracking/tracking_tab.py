import tkinter as tk
from tkinter import ttk
import time
import threading
from collections import defaultdict
from database import setup_database, record_window_activity
from tracking.utils import format_time, load_process_icon, get_window_info

# Define a unified color scheme and font settings
PRIMARY_COLOR = "#007BFF"
PRIMARY_ACTIVE = "#66A2FF"
STOP_COLOR = "#FF4136"
STOP_ACTIVE = "#FF6F61"
BG_COLOR = "#F5F5F5"
TEXT_COLOR = "#333333"
SUCCESS_COLOR = "#28A745"
ERROR_COLOR = "#DC3545"

# Global variables for tracking state
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

def toggle_tracking(tree, tracking_button, status_label, timer_label, root_frame):
    """Toggle the tracking state and update UI accordingly."""
    global tracking_active, session_start_time, window_times, current_windows

    tracking_active = not tracking_active
    if tracking_active:
        session_start_time = time.time()
        threading.Thread(target=tracking_thread, daemon=True).start()
        tracking_button.config(
            text="⏹ Stop Tracking", 
            background=STOP_COLOR, 
            activebackground=STOP_ACTIVE
        )
        status_label.config(text="Tracking Active", fg=SUCCESS_COLOR)
        tree.delete(*tree.get_children())
        window_times.clear()
        current_windows.clear()
    else:
        session_start_time = None
        tracking_button.config(
            text="▶ Start Tracking", 
            background=PRIMARY_COLOR, 
            activebackground=PRIMARY_ACTIVE
        )
        status_label.config(text="Tracking Paused", fg=ERROR_COLOR)

    update_timer(timer_label)
    update_tracking_data(tree, root_frame)

def update_tracking_data(tree, root_frame):
    """Update the treeview with the current tracking data while preserving the open state."""
    if not tracking_active:
        return

    # Preserve the open/closed state of each process node by process name.
    open_states = {}
    for item in tree.get_children():
        # Assume that the first value (Process Name) is unique per process node.
        process_name = tree.item(item, "values")[0]
        open_states[process_name] = tree.item(item, "open")

    # Update window times for any active windows.
    current_time = time.time()
    for window_key, start_time in list(current_windows.items()):
        elapsed = current_time - start_time
        window_times[window_key] += elapsed
        process_name, window_title = window_key.split('|', 1)
        record_window_activity(window_title, process_name, elapsed)
        current_windows[window_key] = current_time

    # Clear and repopulate the Treeview.
    tree.delete(*tree.get_children())
    process_groups = defaultdict(list)
    for window_key, time_spent in window_times.items():
        process_name, window_title = window_key.split('|', 1)
        process_groups[process_name].append((window_title, time_spent))

    for process_name, windows in process_groups.items():
        total_time = sum(t for _, t in windows)
        icon_image = load_process_icon(process_name, process_icons)
        # Restore the open state if it was expanded before.
        process_item = tree.insert(
            "", "end", text="",
            values=(process_name, format_time(total_time)),
            image=icon_image,
            open=open_states.get(process_name, False)
        )
        # Insert each window as a child node.
        for window_title, time_spent in sorted(windows, key=lambda x: x[1], reverse=True):
            tree.insert(process_item, "end", text="", values=(window_title, format_time(time_spent)))
    
    # Schedule the next update.
    root_frame.after(1000, update_tracking_data, tree, root_frame)


def tracking_tab(parent):
    """Create and return the tracking tab frame with an alternative layout."""
    global process_icons
    setup_database()

    # Main frame with a consistent background
    root_frame = tk.Frame(parent, bg=BG_COLOR)
    root_frame.pack(fill="both", expand=True)

    # --- Header Section ---
    header_frame = tk.Frame(root_frame, bg=BG_COLOR)
    header_frame.pack(fill="x", pady=(20, 10))
    
    # Timer label (large, centered)
    timer_label = tk.Label(
        header_frame, text="00:00:00",
        font=("Helvetica", 36, "bold"),
        bg=BG_COLOR, fg=TEXT_COLOR
    )
    timer_label.pack(pady=(0, 5))
    
    # Tracking status label (centered beneath the timer)
    status_label = tk.Label(
        header_frame, text="Tracking Paused",
        font=("Helvetica", 14, "italic"),
        bg=BG_COLOR, fg=ERROR_COLOR
    )
    status_label.pack()

    # --- Control Button Section ---
    # Center the start/stop button below the header
    button_frame = tk.Frame(root_frame, bg=BG_COLOR)
    button_frame.pack(pady=20)
    tracking_button = tk.Button(
        button_frame,
        text="▶ Start Tracking",
        font=("Helvetica", 14, "bold"),
        bg=PRIMARY_COLOR, fg="#FFF",
        padx=20, pady=10,
        relief="flat",
        activebackground=PRIMARY_ACTIVE,
        activeforeground="#FFF",
        command=lambda: toggle_tracking(tree, tracking_button, status_label, timer_label, root_frame)
    )
    tracking_button.pack()

    # --- Data Display: Treeview ---
    data_frame = tk.Frame(root_frame, bg="#FFFFFF", relief="groove", bd=2)
    data_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Configure the ttk style for the Treeview
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", rowheight=40, font=("Helvetica", 10))
    style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"), foreground=TEXT_COLOR)
    
    tree = ttk.Treeview(
        data_frame,
        columns=("Process Name", "Time Spent"),
        show="tree headings"
    )
    tree.pack(fill="both", expand=True, padx=5, pady=5)

    # Configure Treeview columns
    tree.heading("#0", text="Icon", anchor="center")
    tree.heading("Process Name", text="Process Name")
    tree.heading("Time Spent", text="Time Spent")
    tree.column("#0", width=80, anchor="center")
    tree.column("Process Name", width=200, anchor="center")
    tree.column("Time Spent", width=120, anchor="center")

    process_icons = {}
    return root_frame
