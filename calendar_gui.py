import tkinter as tk
from tracking.tracking_tab import tracking_tab
from analytics_tab import analytics_tab
from PIL import Image, ImageTk

def create_gui_calendar():
    root = tk.Tk()
    root.title("Time Tracker Dashboard")
    root.geometry("1200x700")
    root.configure(bg="#f5f5f5")

    # Sidebar setup
    sidebar = tk.Frame(root, width=220, bg="#2C3E50", height=700, relief="flat")
    sidebar.pack(side="left", fill="y")
    sidebar_inner = tk.Frame(sidebar, bg="#2C3E50")
    sidebar_inner.pack(expand=True)

    # Main content area
    content_frame = tk.Frame(root, bg="#f5f5f5", relief="flat")
    content_frame.pack(side="right", expand=True, fill="both")

    active_tab = "Track"
    tab_names = ["Track", "Analytics"]
    button_data = [
        {"text": "Tracker", "icon": "icons/track_icon.png", "tab": "Track"},
        {"text": "Analytics", "icon": "icons/analytics_icon.png", "tab": "Analytics"},
    ]
    buttons = []

    def create_button(text, icon_path, tab_name, selected_tab):
        """Creates a styled sidebar button with an icon and hover effects."""
        def on_enter(event):
            btn.config(bg="#34495E")
        def on_leave(event):
            if selected_tab != tab_name:
                btn.config(bg="#2C3E50")
        
        # Resize and load the icon
        icon_image = Image.open(icon_path).resize((40, 40), Image.ANTIALIAS)
        icon = ImageTk.PhotoImage(icon_image)

        btn = tk.Button(
            sidebar_inner,
            text=f"  {text}",
            image=icon,
            compound="left",
            bg="#2C3E50",
            fg="#ECF0F1",
            font=("Helvetica", 14),
            bd=0,
            highlightthickness=0,
            anchor="w",
            padx=20,
            pady=10,
            relief="flat",
            command=lambda: switch_tab(tab_name)
        )
        btn.image = icon  # Prevent garbage collection
        btn.pack(fill="x", pady=5)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        if selected_tab == tab_name:
            btn.config(bg="#1ABC9C")
        return btn

    def switch_tab(tab_name):
        """Switches to the selected tab and updates the content and sidebar styles."""
        nonlocal active_tab
        active_tab = tab_name
        # Clear the content frame
        for widget in content_frame.winfo_children():
            widget.destroy()
        # Load the selected tab's content
        if tab_name == "Track":
            tracking_tab(content_frame)
        elif tab_name == "Analytics":
            analytics_tab(content_frame)
        update_sidebar_buttons()

    def update_sidebar_buttons():
        """Update sidebar button colors based on the active tab."""
        for btn, name in zip(buttons, tab_names):
            btn.config(bg="#1ABC9C" if active_tab == name else "#2C3E50")

    # Create sidebar buttons
    for data in button_data:
        buttons.append(create_button(data["text"], data["icon"], data["tab"], active_tab))

    # Start with the default tab
    switch_tab("Track")
    root.mainloop()
