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

tracking_active = False

def tracking_thread():
    """Thread function to track window activity"""
    global tracking_active
    current_window = None
    current_process = None
    start_time = time.time()
    
    try:
        while tracking_active:
            hwnd = win32gui.GetForegroundWindow()
            new_window = win32gui.GetWindowText(hwnd)
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            new_process = psutil.Process(pid).name()

            if new_window != current_window or new_process != current_process:
                if current_window is not None:
                    time_spent = time.time() - start_time
                    log_window_time(current_window, current_process, time_spent)
                
                current_window = new_window
                current_process = new_process
                start_time = time.time()

            time.sleep(1) # TODO: Change that if needed
            
        if current_window is not None:
            time_spent = time.time() - start_time
            log_window_time(current_window, current_process, time_spent)
            
    except Exception as e:
        print(f"Error in tracking thread: {e}")

def tracking_tab(parent):
    global tracking_active
    tracking_active = False
    start_time = None

    # Ensure database is set up
    try:
        setup_database()
    except Exception as e:
        print(f"Failed to setup database: {e}")

    def update_timer():
        if tracking_active:
            elapsed_time = int(time.time() - start_time)
            hours = elapsed_time // 3600
            minutes = (elapsed_time % 3600) // 60
            seconds = elapsed_time % 60
            timer_label.config(text=f"{hours:02}:{minutes:02}:{seconds:02}")
            timer_label.after(1000, update_timer)

    def update_tracking_data():
        if tracking_active:
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process_name = psutil.Process(pid).name()

            # Check if the process group exists
            if process_name not in process_tree_items:
                icon_path = download_process_icon(process_name)
                icon_image = None

                if icon_path and os.path.exists(icon_path):
                    try:
                        pil_image = Image.open(icon_path)
                        pil_image = pil_image.resize((30, 30), Image.Resampling.LANCZOS)
                        icon_image = PhotoImage(file=icon_path)
                    except Exception as e:
                        print(f"Failed to load icon for {process_name}: {e}")
                
                # Add a new process group with the icon
                process_tree_items[process_name] = tree.insert(
                    "", "end", text=process_name, image=icon_image, open=True
                )
                if icon_image:
                    process_icons[process_name] = icon_image  # Store reference to prevent garbage collection

            # Add a new window title under the process group
            timestamp = time.strftime("%H:%M:%S")
            tree.insert(
                process_tree_items[process_name], "end",
                text=f"{window_title} [{timestamp}]"
            )

            # Update the view to show new data
            tree.yview_moveto(1.0)

            if tracking_active:
                frame.after(1000, update_tracking_data)

    def toggle_tracking():
        global tracking_active
        nonlocal start_time
        tracking_active = not tracking_active

        if tracking_active:
            # Clear previous history
            tree.delete(*tree.get_children())
            process_tree_items.clear()
            process_icons.clear()

            # Start new tracking session
            thread = threading.Thread(target=tracking_thread, daemon=True)
            thread.start()
            start_time = time.time()
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
    style.configure("Treeview", rowheight=50)  # Set row height to fit the icon

    # Treeview for grouped processes
    tree = ttk.Treeview(data_frame)
    tree.pack(fill="both", expand=True, padx=5, pady=5)

    # Dictionaries to store process groups and icons
    process_tree_items = {}
    process_icons = {}

    return frame
