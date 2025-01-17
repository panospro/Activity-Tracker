from calendar_gui import create_gui_calendar

# TODO: Find a way to run it without having vscode open (pyinstaller)
# TODO: Sync the timers in tracking
# TODO: See if that approach takes lots of resources
def main():
    # NOTE: These dont work here place them where i setupdb
    # drop_tables()
    # clear_other_category_data()
    create_gui_calendar()

if __name__ == '__main__':
    main()