from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from database import fetch_time_by_category_for_date, fetch_time_by_category_for_week
from plots import plot_bar_chart

def analytics_tab(notebook):
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

        plt.clf()

        if not data:
            tk.Label(plot_frame, text="No data available.", font=("Arial", 14), bg="#f9f9f9").pack(pady=20)
            return

        plot_bar_chart(data, title, xlabel="Category", ylabel="Time (minutes)")

        fig = plt.gcf()
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        canvas.draw()

    # Frame for the second tab
    second_tab = ttk.Frame(notebook)
    notebook.add(second_tab, text="Analytics")

    # Calendar
    calendar_frame = ttk.Frame(second_tab)
    calendar_frame.pack(side="left", fill="y", padx=20, pady=20)

    ttk.Label(calendar_frame, text="Select a Date", font=("Helvetica", 18, "bold")).pack(pady=20)
    calendar = Calendar(calendar_frame, selectmode="day", date_pattern="yyyy-mm-dd", font=("Helvetica", 12))
    calendar.pack(pady=10)

    # Buttons for viewing day/week analytics
    btn_frame = ttk.Frame(calendar_frame)
    btn_frame.pack(pady=20)
    ttk.Button(btn_frame, text="View Day", command=lambda: show_data(False)).pack(side="left", padx=15)
    ttk.Button(btn_frame, text="View Week", command=lambda: show_data(True)).pack(side="left", padx=15)

    # Plot frame for analytics
    plot_frame = ttk.Frame(second_tab, borderwidth=2, relief="solid")
    plot_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    return second_tab
