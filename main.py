from database import setup_database
from tracker import track_active_window
from calendar_gui import create_gui_calendar

# TODO: Make better graphs because if lots of categories its messy
# TODO: Find a way to run it without having vscode open (pyinstaller)
# TODO: See if that approach takes lots of resources

# NOTE: Use plotly for hoverable tooltips showing additional information (e.g., exact percentages and totals).
def main():
    setup_database()

    # drop_tables()
    # clear_other_category_data()

    try:
        track_active_window()  # Start tracking windows
    except KeyboardInterrupt:
        print("\nTracking stopped by user.")

if __name__ == '__main__':
    create_gui_calendar()