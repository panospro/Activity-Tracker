import tkinter as tk
from tracker import track_active_window
import time

def tracking_tab(parent):
    tracking_active = False  # Initialize tracking state
    start_time = None  # To store the starting time

    def update_timer():
        if tracking_active:
            elapsed_time = int(time.time() - start_time)
            hours = elapsed_time // 3600
            minutes = (elapsed_time % 3600) // 60
            seconds = elapsed_time % 60
            timer_label.config(text=f"{hours:02}:{minutes:02}:{seconds:02}")
            timer_label.after(1000, update_timer)  # Update every second

    def toggle_tracking():
        nonlocal tracking_active, start_time
        tracking_active = not tracking_active

        if tracking_active:
            track_active_window(True)
            start_time = time.time()  # Record the start time
            tracking_button.config(
                text="⏹ Stop Tracking", bg="#FF4136", activebackground="#FF6F61"
            )
            status_label.config(text="Tracking is ON", fg="#28A745")
            update_timer()  # Start the timer
        else:
            track_active_window(False)
            tracking_button.config(
                text="▶ Start Tracking", bg="#007BFF", activebackground="#66A2FF"
            )
            status_label.config(text="Tracking is OFF", fg="#DC3545")

    # Main frame for the tab
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

    # Placeholder for tracking data
    data_frame = tk.Frame(frame, bg="#FFFFFF", relief="groove", bd=2)
    data_frame.pack(fill="both", expand=True, padx=20, pady=20)

    placeholder_label = tk.Label(
        data_frame,
        text="Tracking data will appear here.",
        font=("Helvetica", 12),
        bg="#FFFFFF",
        fg="#666",
    )
    placeholder_label.pack(pady=10)

    return frame
