import tkinter as tk
import time
import psutil
import win32gui
import win32process
from PIL import Image
import os 
import threading
from database import setup_database, log_window_time
from utils import download_process_icon
from tkinter import ttk, PhotoImage
from collections import defaultdict

tracking_active = False
window_times = defaultdict(float)  # Store cumulative time for each window
current_windows = {}  # Store current window sessions
session_start_time = None  # Global start time for the session

def is_valid_window(hwnd):
    """Check if the window is valid for tracking"""
    try:
        if not hwnd or hwnd == 0:
            return False
            
        # Check if window is visible
        if not win32gui.IsWindowVisible(hwnd):
            return False
            
        # Get window title
        title = win32gui.GetWindowText(hwnd)
        if not title:
            return False
            
        # Try to get process ID
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if pid <= 0:
            return False
            
        # Try to get process name
        try:
            process = psutil.Process(pid)
            process_name = process.name()
            if not process_name:
                return False
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
            
        return True
    except Exception:
        return False

def get_window_info():
    """Get current window information with error handling"""
    try:
        hwnd = win32gui.GetForegroundWindow()
        
        if not is_valid_window(hwnd):
            return None
            
        window_title = win32gui.GetWindowText(hwnd)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process_name = psutil.Process(pid).name()
        
        return {
            'window_title': window_title,
            'process_name': process_name,
            'window_key': f"{process_name}|{window_title}"
        }
    except Exception as e:
        print(f"Error getting window info: {e}")
        return None

def tracking_thread():
    """Thread function to track window activity"""
    global tracking_active, window_times, current_windows, last_valid_window
    
    try:
        while tracking_active:
            current_info = get_window_info()
            
            if current_info is None:
                # If current window is invalid, use last valid window
                if last_valid_window:
                    current_info = last_valid_window
            else:
                # Update last valid window
                last_valid_window = current_info
            
            if current_info:
                window_key = current_info['window_key']
                current_time = time.time()
                
                # Update time for current window and log if switched
                if window_key in current_windows:
                    elapsed = current_time - current_windows[window_key]
                    window_times[window_key] += elapsed
                    # Log the activity when switching windows
                    log_window_time(
                        current_info['window_title'],
                        current_info['process_name'],
                        elapsed
                    )
                
                # Reset current window time
                current_windows.clear()
                current_windows[window_key] = current_time

            time.sleep(1)
            
    except Exception as e:
        print(f"Error in tracking thread: {e}")
        # Don't stop tracking on error, just log it and continue
        if tracking_active:
            thread = threading.Thread(target=tracking_thread, daemon=True)
            thread.start()

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

def tracking_tab(parent):
    global tracking_active, window_times, session_start_time
    tracking_active = False

    try:
        setup_database()
    except Exception as e:
        print(f"Failed to setup database: {e}")

    def get_session_time():
        """Get the current session duration"""
        if not session_start_time or not tracking_active:
            return 0
        return time.time() - session_start_time

    def update_timer():
        """Update the main timer display"""
        if tracking_active:
            elapsed_time = int(get_session_time())
            hours = elapsed_time // 3600
            minutes = (elapsed_time % 3600) // 60
            seconds = elapsed_time % 60
            timer_label.config(text=f"{hours:02}:{minutes:02}:{seconds:02}")
            timer_label.after(1000, update_timer)

    def update_tracking_data():
        """Update the treeview with current tracking data"""
        if tracking_active:
            # Update current window's time
            current_time = time.time()

            # Create a copy of the dictionary to iterate safely
            current_windows_copy = current_windows.copy()

            for window_key, start_time in current_windows_copy.items():
                elapsed = current_time - start_time
                window_times[window_key] += elapsed
                # Get window title and process name from the key
                process_name, window_title = window_key.split('|', 1)
                # Log the activity
                log_window_time(window_title, process_name, elapsed)
                current_windows[window_key] = current_time

            # Clear existing items
            tree.delete(*tree.get_children())

            # Group windows by process
            process_groups = defaultdict(list)
            for window_key, time_spent in window_times.items():
                process_name, window_title = window_key.split('|', 1)
                process_groups[process_name].append((window_title, time_spent))

            # Update treeview with grouped data
            for process_name, windows in process_groups.items():
                # Get or create process icon
                icon_image = None
                if process_name not in process_icons:
                    icon_path = download_process_icon(process_name)
                    if icon_path and os.path.exists(icon_path):
                        try:
                            pil_image = Image.open(icon_path)
                            pil_image = pil_image.resize((30, 30), Image.Resampling.LANCZOS)
                            icon_image = PhotoImage(file=icon_path)
                            process_icons[process_name] = icon_image
                        except Exception as e:
                            print(f"Failed to load icon for {process_name}: {e}")
                else:
                    icon_image = process_icons[process_name]

                # Create process group
                total_time = sum(time for _, time in windows)
                process_item = tree.insert(
                    "", "end",
                    text=f"{process_name} (Total: {format_time(total_time)})",
                    image=icon_image,
                    open=True
                )

                # Add window entries under process group
                for window_title, time_spent in sorted(windows, key=lambda x: x[1], reverse=True):
                    tree.insert(
                        process_item,
                        "end",
                        text=f"{window_title} ({format_time(time_spent)})"
                    )

            if tracking_active:
                frame.after(1000, update_tracking_data)


    def toggle_tracking():
        global tracking_active, window_times, session_start_time
        
        # If we're stopping tracking, log final times
        if tracking_active:
            current_time = time.time()
            for window_key, start_time in current_windows.items():
                process_name, window_title = window_key.split('|', 1)
                final_time = current_time - start_time
                if final_time > 0:
                    log_window_time(window_title, process_name, final_time)
        
        tracking_active = not tracking_active

        if tracking_active:
            # Clear previous data
            tree.delete(*tree.get_children())
            process_icons.clear()
            window_times.clear()
            current_windows.clear()
            
            # Set session start time
            session_start_time = time.time()

            # Start new tracking session
            thread = threading.Thread(target=tracking_thread, daemon=True)
            thread.start()
            
            tracking_button.config(
                text="⏹ Stop Tracking",
                bg="#FF4136",
                activebackground="#FF6F61"
            )
            status_label.config(text="Tracking is ON", fg="#28A745")
            update_timer()
            update_tracking_data()
        else:
            tracking_button.config(
                text="▶ Start Tracking",
                bg="#007BFF",
                activebackground="#66A2FF"
            )
            status_label.config(text="Tracking is OFF", fg="#DC3545")
            session_start_time = None

    # Main frame
    frame = tk.Frame(parent, bg="#F5F5F5")
    frame.pack(fill="both", expand=True)

    # Timer Label
    timer_label = tk.Label(
        frame,
        text="00:00:00",
        font=("Helvetica", 36, "bold"),
        bg="#F5F5F5",
        fg="#333",
    )
    timer_label.pack(pady=20)

    # Status label
    status_label = tk.Label(
        frame,
        text="Tracking is OFF",
        font=("Helvetica", 14, "italic"),
        bg="#F5F5F5",
        fg="#DC3545",
    )
    status_label.pack(pady=10)

    # Start/Stop Tracking Button
    tracking_button = tk.Button(
        frame,
        text="▶ Start Tracking",
        command=toggle_tracking,
        font=("Helvetica", 14, "bold"),
        bg="#007BFF",
        fg="#FFF",
        padx=20,
        pady=10,
        relief="flat",
        activebackground="#66A2FF",
        activeforeground="#FFF",
    )
    tracking_button.pack(pady=20)

    # Data frame
    data_frame = tk.Frame(frame, bg="#FFFFFF", relief="groove", bd=2)
    data_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Style Treeview for row height
    style = ttk.Style()
    style.configure("Treeview", rowheight=50)

    # Treeview for grouped processes
    tree = ttk.Treeview(data_frame)
    tree.pack(fill="both", expand=True, padx=5, pady=5)

    # Dictionary to store process icons
    process_icons = {}

    return frame