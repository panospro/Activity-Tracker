import sqlite3
import win32gui
import win32process
import psutil
import matplotlib.pyplot as plt

# **Active Window Tracker**
def get_active_window_title():
    try:
        hwnd = win32gui.GetForegroundWindow()  # Active window handle
        window_title = win32gui.GetWindowText(hwnd)  # Active window title

        if window_title:
            return window_title

        # Retrieve process ID if title is empty
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process_name = psutil.Process(pid).name()
        return f"Unknown Window (Process: {process_name})"
    except Exception as e:
        return f"Error retrieving window title: {e}"
    
# **Log Activity**
def log_activity(window_title):
    with sqlite3.connect('time_tracking.db') as conn:
        conn.execute(
            '''
            INSERT INTO activity_logs (timestamp, window_title, category)
            VALUES (datetime('now'), ?, NULL)
            ''', 
            (window_title,)
        )

# **Generate and Plot Data**
def plot_activity_summary():
    with sqlite3.connect('time_tracking.db') as conn:
        data = conn.execute(
            '''
            SELECT category, COUNT(*) as count 
            FROM activity_logs 
            WHERE category IS NOT NULL
            GROUP BY category
            '''
        ).fetchall()

    if not data:
        print("No data available to generate a report.")
        return

    categories = [row[0] or 'Uncategorized' for row in data]
    counts = [row[1] for row in data]

    plt.pie(counts, labels=categories, autopct='%1.1f%%', startangle=140)
    plt.title('Time Spent by Category')
    plt.show()