from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from database import fetch_time_by_category_for_date, fetch_time_by_category_for_week
from plots import plot_bar_chart

def analytics_tab(parent):
    # Configure overall style
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background="#f5f5f5")
    style.configure("TLabel", background="#f5f5f5", font=("Helvetica", 12))
    style.configure("Title.TLabel", font=("Helvetica", 24, "bold"), foreground="#333")
    style.configure("TButton", font=("Helvetica", 12), padding=5)

    def show_data(is_week=False):
        selected_date = calendar.get_date()
        try:
            date_obj = datetime.strptime(selected_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid Date", "Please select a valid date.")
            return

        if is_week:
            start_date = date_obj - timedelta(days=date_obj.weekday())
            end_date = start_date + timedelta(days=6)
            data = fetch_time_by_category_for_week(start_date.strftime("%Y-%m-%d"),
                                                   end_date.strftime("%Y-%m-%d"))
            title_text = f"Activity for Week\n{start_date.date()} to {end_date.date()}"
        else:
            data = fetch_time_by_category_for_date(selected_date)
            title_text = f"Activity for\n{selected_date}"
        display_data(data, title_text)

    def display_data(data, title_text):
        # Clear previous plot
        for widget in plot_frame.winfo_children():
            widget.destroy()
        plt.clf()

        if not data:
            tk.Label(plot_frame, text="No data available.",
                     font=("Helvetica", 14), bg="#f5f5f5").pack(pady=20)
            return

        plot_bar_chart(data, title_text, xlabel="Category", ylabel="Time (minutes)")
        canvas = FigureCanvasTkAgg(plt.gcf(), master=plot_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        canvas.draw()

    # Main container frame
    main_frame = ttk.Frame(parent, padding=20)
    main_frame.pack(fill="both", expand=True)

    # Header label
    ttk.Label(main_frame, text="Analytics", style="Title.TLabel", anchor="center") \
        .pack(pady=(0, 20))

    # Content frame containing calendar and plot
    content_frame = ttk.Frame(main_frame)
    content_frame.pack(fill="both", expand=True)

    # Left panel: Calendar and view buttons
    left_panel = ttk.Frame(content_frame)
    left_panel.pack(side="left", fill="y", padx=(0, 20))
    ttk.Label(left_panel, text="Select a Date", font=("Helvetica", 18, "bold")) \
        .pack(pady=(0, 10))

    calendar = Calendar(
        left_panel,
        selectmode="day",
        date_pattern="yyyy-mm-dd",
        font=("Helvetica", 12),
        background="#ffffff",
        bordercolor="#d9d9d9",
        headersbackground="#ececec",
        normalbackground="#f5f5f5",
        foreground="#333333"
    )
    calendar.pack(pady=10)

    btn_frame = ttk.Frame(left_panel)
    btn_frame.pack(pady=20)
    ttk.Button(btn_frame, text="View Day", command=lambda: show_data(False)) \
        .pack(side="left", padx=10)
    ttk.Button(btn_frame, text="View Week", command=lambda: show_data(True)) \
        .pack(side="left", padx=10)

    # Right panel: Plot display
    plot_frame = ttk.Frame(content_frame, borderwidth=1, relief="solid")
    plot_frame.pack(side="right", fill="both", expand=True, padx=(20, 0))

    # Preload data for the current day
    show_data(False)
