import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import MaxNLocator, FuncFormatter

def fetch_data(query, params=()):
    """Fetch data from the SQLite database."""
    with sqlite3.connect('time_tracking.db') as conn:
        return conn.execute(query, params).fetchall()

def plot_pie_chart(data, title, ax=None):
    """Generate a donut-style pie chart."""
    counts = [row[1] for row in data]
    labels = [row[0] or 'Unnamed' for row in data]
    colors = cm.tab20c(np.linspace(0, 1, len(labels)))
    ax = ax or plt.gca()
    
    wedges, texts, autotexts = ax.pie(
        counts, labels=labels, autopct='%1.1f%%', startangle=140,
        colors=colors, pctdistance=0.85
    )
    for text in texts:
        text.set(fontsize=10, weight="bold")
    for autotext in autotexts:
        autotext.set(fontsize=10, weight="bold", color="white")
    
    # Add a white circle in the center for a donut effect
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    ax.add_artist(centre_circle)
    ax.set_title(title, fontsize=14, weight="bold")

def plot_bar_chart(data, title, xlabel, ylabel, ax=None):
    """Generate a bar chart."""
    labels, values = zip(*[(row[0] or 'Unnamed', row[1]) for row in data])
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
    colors = cm.tab20c(np.linspace(0, 1, len(labels)))
    ax.bar(labels, values, color=colors, width=0.5)
    
    ax.set_title(title, fontsize=14, weight="bold")
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.tick_params(axis="x", labelrotation=45, labelsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    ax.yaxis.set_major_locator(MaxNLocator(nbins=5))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x/60:.1f}m"))
    
    return ax.figure

def plot_activity_summary():
    """Display an activity summary with a bar chart for total time per category"""
    category_data = fetch_data(
        '''SELECT category, SUM(time_spent) FROM activity_logs 
           WHERE category IS NOT NULL GROUP BY category'''
    )
    other_data = fetch_data(
        '''SELECT window_title, SUM(time_spent) FROM activity_logs 
           WHERE category = "Other" GROUP BY window_title'''
    )

    if not category_data:
        print("No data available to generate a report.")
        return

    num_plots = 2 if other_data else 1
    fig, axes = plt.subplots(num_plots, 1, figsize=(14, 7), constrained_layout=True)
    # Ensure axes is iterable even when there's only one subplot.
    if num_plots == 1:
        axes = [axes]

    plot_bar_chart(
        category_data,
        title="Total Time Spent by Category",
        xlabel="Category",
        ylabel="Time (seconds)",
        ax=axes[0]
    )
    if other_data:
        plot_pie_chart(
            other_data,
            title='Time Spent on "Other" Category',
            ax=axes[1]
        )
    plt.show()
