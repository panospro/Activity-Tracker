from database import setup_database, categorize_data, drop_tables, clear_other_category_data
from plots import plot_activity_summary
from tracker import track_active_window
from calendar_gui import create_gui_calendar

# TODO: Make better graphs because if lots of categories its messy
# TODO: Make the graphs per day or something
# TODO: Find a way to run it without having vscode open (pyinstaller)
# TODO: See if that approach takes lots of resources

# NOTE: Use plotly for hoverable tooltips showing additional information (e.g., exact percentages and totals).
# NOTE: Highlight the largest slice by exploding it slightly
def main():
    setup_database()

    # drop_tables()
    # clear_other_category_data()

    try:
        track_active_window()  # Start tracking windows
    except KeyboardInterrupt:
        print("\nTracking stopped by user.")
    finally:
        # Ensure these steps always run after tracking, even if interrupted
        categorize_data()  # Categorize logged data

        print("Generating report...")
        plot_activity_summary()  # Generate and display the report

if __name__ == '__main__':
    main()
    create_gui_calendar()
