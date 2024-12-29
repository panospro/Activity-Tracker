import time
from database import setup_database, categorize_data, drop_tables, clear_other_category_data
from tracker import get_active_window_title, log_activity, plot_activity_summary

# TODO: Make better graphs because if lots of categories its messy, then make it per day or something
# TODO: Find a simpler way to do it and maybe recognize the windows that are open instead of adding them by hand one by one and maybe keep track of time they are open instead of doing random 5 sec intervals  
# TODO: Find a way to run it without having vscode open

# **Main Script**
def main():
    setup_database()

    # drop_tables()
    # clear_other_category_data()

    print("Tracking started. Press Ctrl+C to stop and generate report.")
    try:
        while True:
            window_title = get_active_window_title()
            log_activity(window_title)
            time.sleep(1)  # Log every 5 seconds
    except KeyboardInterrupt:
        print("\nCategorizing data...")
        categorize_data()
        print("Generating report...")
        plot_activity_summary()

if __name__ == '__main__':
    main()
