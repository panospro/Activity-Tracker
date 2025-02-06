from calendar_gui import create_gui_calendar

# NOTE: Last update: 
# 1) Move the contents of everything in C:\Delete-Later (maybe not needed)
# 2) Run the command python -m nuitka --standalone --msvc=latest --enable-plugin=tk-inter --include-data-dir=icons=icons main.py 
# 3) Send the main.dist as zip to someone to run the app
# 4) Run main.exe

# TODO: Remove the console from the user while running the .exe
# TODO: Find out why for some reason it doesnt run without the python icon named default icon 
# TODO: Do something with the calendar, show them grouped by .exe
if __name__ == '__main__':
    create_gui_calendar()