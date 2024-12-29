import sqlite3

# **Database Setup**
def setup_database():
    with sqlite3.connect('time_tracking.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                window_title TEXT,
                category TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT,
                category TEXT
            )
        ''')

# **Clear 'Other' Category Data**
def clear_other_category_data():
    with sqlite3.connect('time_tracking.db') as conn:
        conn.execute('DELETE FROM activity_logs WHERE category = ?', ('Other',))

# **Clear Database**
def drop_tables():
    with sqlite3.connect('time_tracking.db') as conn:
        conn.execute('DROP TABLE IF EXISTS activity_logs')
        conn.execute('DROP TABLE IF EXISTS categories')

# **Remove Specific Logs**
def remove_specific_logs(cursor, window_titles_to_remove):
    query = "DELETE FROM activity_logs WHERE " + " OR ".join(
        ["window_title LIKE ?" for _ in window_titles_to_remove]
    )
    cursor.execute(query, tuple(f"%{title}%" for title in window_titles_to_remove))
    print("Logs with specified titles have been removed.")

def categorize_data():
    window_titles_to_remove = [
        "Εναλλαγή εργασιών", "Selected Tab",
        "Error retrieving window title: pid must be a positive integer (got -1238378576)",
        "Διαχείριση Εργασιών", "Unknown Window (Process: explorer.exe)"
    ]

    keyword_to_category = {
        "visual studio code": "Visual Studio Code",
        "youtube": "YouTube",
        "discord": "Discord",
        "facebook": "Facebook",
        "google chrome": "Google Chrome",
        "Postman": "Postman",
        "GitHub Desktop": "GitHub Desktop",
        "MongoDB Compass": "MongoDB Compass",
        "Notepad++": "Notepad++",
        "League of Legends": "League of Legends"
    }

    with sqlite3.connect('time_tracking.db') as conn:
        cursor = conn.cursor()

        # Remove specific logs
        remove_specific_logs(cursor, window_titles_to_remove)

        # Fetch all uncategorized logs
        cursor.execute('SELECT id, window_title FROM activity_logs WHERE category IS NULL')
        logs = cursor.fetchall()
        print("Uncategorized Logs:", logs)

        # Update categories based on keywords
        for log_id, window_title in logs:
            category = next(
                (mapped_category for keyword, mapped_category in keyword_to_category.items()
                 if keyword.lower() in window_title.lower()), "Other"  # Default to 'Other' if no category matches
            )
            cursor.execute('UPDATE activity_logs SET category = ? WHERE id = ?', (category, log_id))

        conn.commit()

        # Fetch and print logs categorized as 'Other'
        cursor.execute('SELECT id, window_title FROM activity_logs WHERE category = "Other"')
        other_logs = cursor.fetchall()
        print("\nLogs categorized as 'Other':", other_logs)

    print("Categorization complete.")
