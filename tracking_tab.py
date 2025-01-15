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

            time.sleep(1)
            
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

            if window_title != history_frame.current_window or process_name != history_frame.current_process:
                try:
                    # Create new entry frame for this activity
                    entry_frame = tk.Frame(history_frame, bg="#FFFFFF", relief="ridge", bd=1)
                    entry_frame.pack(fill="x", padx=5, pady=2)
                    
                    # Add timestamp
                    timestamp = time.strftime("%H:%M:%S")
                    time_label = tk.Label(
                        entry_frame,
                        text=timestamp,
                        font=("Helvetica", 10),
                        bg="#FFFFFF",
                        fg="#666"
                    )
                    time_label.pack(side="left", padx=5)
                    
                    # Try to load and display icon
                    icon_path = download_process_icon(process_name)
                    if icon_path and os.path.exists(icon_path):
                        pil_image = Image.open(icon_path)
                        pil_image = pil_image.resize((16, 16), Image.Resampling.LANCZOS)
                        tk_image = tk.PhotoImage(file=icon_path)
                        icon_label = tk.Label(
                            entry_frame,
                            image=tk_image,
                            bg="#FFFFFF"
                        )
                        icon_label.image = tk_image
                        icon_label.pack(side="left", padx=5)
                    
                    # Add window title and process name
                    info_label = tk.Label(
                        entry_frame,
                        text=f"{window_title} ({process_name})",
                        font=("Helvetica", 10),
                        bg="#FFFFFF",
                        fg="#333",
                        anchor="w"
                    )
                    info_label.pack(side="left", fill="x", expand=True, padx=5)
                    
                    # Update current window/process tracking
                    history_frame.current_window = window_title
                    history_frame.current_process = process_name
                    
                    # Ensure the newest entry is visible
                    history_canvas.yview_moveto(1.0)
                    
                except Exception as e:
                    print(f"Error updating history: {e}")

            if tracking_active:
                frame.after(1000, update_tracking_data)

    def toggle_tracking():
        global tracking_active
        nonlocal start_time
        tracking_active = not tracking_active

        if tracking_active:
            # Clear previous history
            for widget in history_frame.winfo_children():
                widget.destroy()
            history_frame.current_window = None
            history_frame.current_process = None
            
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

    # Create a frame with scrollbar for history
    history_container = tk.Frame(data_frame, bg="#FFFFFF")
    history_container.pack(fill="both", expand=True, padx=5, pady=5)

    # Add a canvas for scrolling
    history_canvas = tk.Canvas(
        history_container,
        bg="#FFFFFF",
        highlightthickness=0
    )
    history_scrollbar = tk.Scrollbar(
        history_container,
        orient="vertical",
        command=history_canvas.yview
    )
    history_frame = tk.Frame(history_canvas, bg="#FFFFFF")
    
    # Configure scrolling
    history_frame.bind(
        "<Configure>",
        lambda e: history_canvas.configure(scrollregion=history_canvas.bbox("all"))
    )
    history_canvas.create_window((0, 0), window=history_frame, anchor="nw")
    history_canvas.configure(yscrollcommand=history_scrollbar.set)
    
    # Pack scrolling components
    history_scrollbar.pack(side="right", fill="y")
    history_canvas.pack(side="left", fill="both", expand=True)
    
    # Add attributes to history_frame to track current window/process
    history_frame.current_window = None
    history_frame.current_process = None

    return frame
