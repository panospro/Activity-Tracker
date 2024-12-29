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

# Fetches data from db
def fetch_data(query, params=()):
    with sqlite3.connect('time_tracking.db') as conn:
        return conn.execute(query, params).fetchall()

# Generates a pie chart
def plot_pie_chart(data, labels, title):
    counts = [row[1] for row in data]
    labels = [row[0] or 'Unnamed' for row in data]
    plt.pie(counts, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title(title)

# Displays the activity summary with all categories and category 'Other'.
def plot_activity_summary():
    category_data = fetch_data(
        '''SELECT category, COUNT(*) FROM activity_logs WHERE category IS NOT NULL GROUP BY category'''
    )
    other_data = fetch_data(
        '''SELECT window_title, COUNT(*) FROM activity_logs WHERE category = "Other" GROUP BY window_title'''
    )

    if not category_data:
        print("No data available to generate a report.")
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    plt.sca(axes[0])
    plot_pie_chart(category_data, 'Category', 'Time Spent by Category')

    plt.sca(axes[1])
    if other_data:
        plot_pie_chart(other_data, 'Window Title', 'Time Spent on "Other" Category')
    else:
        print("No data categorized as 'Other'.")

    plt.tight_layout()
    plt.show()