
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from database import fetch_time_by_category_for_date, fetch_time_by_category_for_week
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

def create_gui_calendar():
    def show_data(is_week=False):
        selected_date = calendar.get_date()
        if is_week:
            start_date = datetime.strptime(selected_date, "%Y-%m-%d") - timedelta(days=datetime.strptime(selected_date, "%Y-%m-%d").weekday())
            end_date = start_date + timedelta(days=6)
            data = fetch_time_by_category_for_week(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
            title = f"Activity for Week {start_date.date()} to {end_date.date()}"
        else:
            data = fetch_time_by_category_for_date(selected_date)
            title = f"Activity for {selected_date}"
        display_data(data, title)

    def display_data(data, title):
        for widget in plot_frame.winfo_children():
            widget.destroy()
        if not data:
            tk.Label(plot_frame, text="No data available.", font=("Arial", 14), bg="#f9f9f9").pack(pady=20)
            return
        fig, ax = plt.subplots(figsize=(8, 4))
        categories, times = zip(*[(row[0] or "Unnamed", row[1]) for row in data])
        ax.bar(categories, times, color="#4CAF50")
        ax.set(title=title, xlabel="Category", ylabel="Time (seconds)")
        ax.tick_params(axis="x", rotation=45, labelsize=10)
        fig.tight_layout(pad=3.0)
        FigureCanvasTkAgg(fig, master=plot_frame).get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    root = tk.Tk()
    root.title("Time Tracking Calendar")
    root.geometry("1000x650")
    root.configure(bg="#f9f9f9")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background="#f9f9f9")
    style.configure("TLabel", background="#f9f9f9", font=("Helvetica", 14))
    style.configure("TButton", font=("Helvetica", 12, "bold"), foreground="#FFFFFF", background="#007BFF", padding=10)
    style.map("TButton", background=[('active', '#0056b3')])

    calendar_frame = ttk.Frame(root)
    calendar_frame.pack(side="left", fill="y", padx=20, pady=20)

    ttk.Label(calendar_frame, text="Select a Date", font=("Helvetica", 16, "bold")).pack(pady=10)
    calendar = Calendar(calendar_frame, selectmode="day", date_pattern="yyyy-mm-dd", font=("Helvetica", 12))
    calendar.pack(pady=10)

    btn_frame = ttk.Frame(calendar_frame)
    btn_frame.pack(pady=20)
    ttk.Button(btn_frame, text="View Day", command=lambda: show_data(False), style="TButton").pack(side="left", padx=10)
    ttk.Button(btn_frame, text="View Week", command=lambda: show_data(True), style="TButton").pack(side="left", padx=10)

    plot_frame = ttk.Frame(root, borderwidth=2, relief="solid")
    plot_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    root.mainloop()
