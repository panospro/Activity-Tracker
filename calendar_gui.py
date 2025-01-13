import tkinter as tk
from tracking_tab import tracking_tab
from analytics_tab import analytics_tab
from PIL import Image, ImageTk

def create_gui_calendar():
    root = tk.Tk()
    root.title("Time Tracker Dashboard")
    root.geometry("1200x700")
    root.configure(bg="#f5f5f5")

    # Sidebar
    sidebar = tk.Frame(root, width=220, bg="#2C3E50", height=700, relief="flat")
    sidebar.pack(side="left", fill="y")

    # Centering frame for buttons in the sidebar
    sidebar_inner = tk.Frame(sidebar, bg="#2C3E50")
    sidebar_inner.pack(expand=True)

    # Sidebar Style
    def create_button(text, icon_path, tab_name, selected_tab):
        """Creates a styled button with an icon and hover effect."""
        def on_enter(event):
            btn.config(bg="#34495E")  # Darker hover background
        def on_leave(event):
            if selected_tab != tab_name:
                btn.config(bg="#2C3E50")  # Original background

        # Increase icon size
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
        btn.image = icon  # Keep a reference to avoid garbage collection
        btn.pack(fill="x", pady=5)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        if selected_tab == tab_name:
            btn.config(bg="#1ABC9C")  # Highlight active tab
        return btn

    def switch_tab(tab_name):
        """Switch to the selected tab and update the active tab highlight."""
        nonlocal active_tab
        active_tab = tab_name
        for widget in content_frame.winfo_children():
            widget.destroy()  # Clear content frame
        if tab_name == "Track":
            tracking_tab(content_frame)
        elif tab_name == "Analytics":
            analytics_tab(content_frame)
        update_sidebar_buttons()

    def update_sidebar_buttons():
        """Refresh sidebar button styles based on active tab."""
        for btn, tab_name in zip(buttons, tab_names):
            if active_tab == tab_name:
                btn.config(bg="#1ABC9C")  # Highlight active tab
            else:
                btn.config(bg="#2C3E50")  # Reset to default background

    # Main Content Area
    content_frame = tk.Frame(root, bg="#f5f5f5", relief="flat")
    content_frame.pack(side="right", expand=True, fill="both")

    # Sidebar Buttons
    active_tab = "Track"
    tab_names = ["Track", "Analytics"]
    button_data = [
        {"text": "Tracker", "icon": "icons/track_icon.png", "tab": "Track"},
        {"text": "Analytics", "icon": "icons/analytics_icon.png", "tab": "Analytics"},
    ]

    buttons = []
    for btn_data in button_data:
        buttons.append(create_button(btn_data["text"], btn_data["icon"], btn_data["tab"], active_tab))

    # Default Tab
    switch_tab("Track")

    root.mainloop()
