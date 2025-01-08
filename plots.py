import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

# Fetches data from db
def fetch_data(query, params=()):
    with sqlite3.connect('time_tracking.db') as conn:
        return conn.execute(query, params).fetchall()

# Generates a pie chart
def plot_pie_chart(data, labels, title):
    counts = [row[1] for row in data]
    labels = [row[0] or 'Unnamed' for row in data]
    colors = cm.tab20c(np.linspace(0, 1, len(labels)))  # Enhanced color scheme

    # Highlight the largest slice by exploding it slightly
    # explode = [0.1 if i == counts.index(max(counts)) else 0 for i in range(len(counts))]

    # Create the pie chart
    wedges, texts, autotexts = plt.pie(
        counts,
        labels=labels,
        autopct='%1.1f%%',
        startangle=140,
        colors=colors,
        # explode=explode,
        pctdistance=0.85,
    )

    # Enhance text aesthetics
    plt.setp(autotexts, size=10, weight="bold", color="white")
    plt.setp(texts, size=10, weight="bold")

    # Add a circle for a donut chart effect
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    plt.gca().add_artist(centre_circle)

    # Set title with custom font
    plt.title(title, fontsize=14, weight="bold")

def plot_bar_chart(data, title, xlabel, ylabel):
    labels, values = zip(*[(row[0] or 'Unnamed', row[1]) for row in data])
    plt.bar(labels, values, color=cm.tab20c(np.linspace(0, 1, len(labels))), width=0.5)
    plt.title(title, fontsize=14, weight="bold")
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.xticks(rotation=0, ha="center", fontsize=10)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()

# Displays the activity summary with all categories and category 'Other'
def plot_activity_summary():
    # Fetch total time spent per category
    category_data = fetch_data(
        '''SELECT category, SUM(time_spent) FROM activity_logs 
           WHERE category IS NOT NULL GROUP BY category'''
    )

    # Fetch detailed data for "Other" category
    other_data = fetch_data(
        '''SELECT window_title, SUM(time_spent) FROM activity_logs 
           WHERE category = "Other" GROUP BY window_title'''
    )

    if not category_data:
        print("No data available to generate a report.")
        return

    # Create subplots dynamically based on available data
    num_plots = 2 if other_data else 1
    fig, axes = plt.subplots(num_plots, 1, figsize=(14, 7), constrained_layout=True)
    # Ensure axes is iterable
    if num_plots == 1:
        axes = [axes]
    # Plot category summary
    plt.sca(axes[0])

    if category_data:
        plot_bar_chart(category_data,title="Total Time Spent by Category",xlabel="Category",ylabel="Time (seconds)")

    # Plot "Other" category if data exists
    if other_data:
        plt.sca(axes[1])
        plot_pie_chart(other_data, 'Window Title', 'Time Spent on "Other" Category')

    plt.show()
