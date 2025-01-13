from tkinter import ttk
from tracker import track_active_window

def tracking_tab(notebook):
    tracking_active = False  # Initialize tracking state

    def toggle_tracking():
        nonlocal tracking_active
        tracking_active = not tracking_active

        if tracking_active:
            track_active_window(True)
            tracking_button.config(text="Stop Tracking")
        else:
            track_active_window(False)
            tracking_button.config(text="Start Tracking")

    # Frame for the first tab
    first_tab = ttk.Frame(notebook)
    notebook.add(first_tab, text="Tracking")

    # Start/Stop Tracking Button
    tracking_button = ttk.Button(
        first_tab,
        text="Start Tracking",
        command=toggle_tracking,
        style="TButton"
    )
    tracking_button.pack(pady=20)

    # Additional widgets for the first tab can go here
    ttk.Label(first_tab, text="Additional content for the first tab.", font=("Helvetica", 14)).pack(pady=20)

    return first_tab
