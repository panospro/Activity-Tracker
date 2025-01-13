import tkinter as tk
from tkinter import ttk
from tracking_tab import tracking_tab
from analytics_tab import analytics_tab

def create_gui_calendar():
    root = tk.Tk()
    root.title("Time Tracking Application")
    root.geometry("1000x650")
    root.configure(bg="#f9f9f9")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TButton", font=("Helvetica", 12, "bold"))

    # Notebook for tabs
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    # Add tabs
    tracking_tab(notebook)
    analytics_tab(notebook)

    root.mainloop()
