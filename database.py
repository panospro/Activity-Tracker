import sqlite3

# **Database Setup**
def setup_database():
    conn = sqlite3.connect('time_tracking.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        window_title TEXT,
        category TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword TEXT,
        category TEXT
    )
    ''')

    conn.commit()
    conn.close()

# **Clear 'other' category data from Database**
def clear_other_category_data():
    conn = sqlite3.connect('time_tracking.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM activity_logs WHERE category = ?', ('Other',))
    conn.commit()
    conn.close()

# **Clear Database**
def drop_tables():
    conn = sqlite3.connect('time_tracking.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS activity_logs')
    cursor.execute('DROP TABLE IF EXISTS categories')
    conn.commit()
    conn.close()

def remove_specific_logs():
    conn = sqlite3.connect('time_tracking.db')
    cursor = conn.cursor()

    # List of window titles to remove
    window_titles_to_remove = ["Εναλλαγή εργασιών", "Selected Tab", "Error retrieving window title: pid must be a positive integer (got -1238378576)", "Διαχείριση Εργασιών","Unknown Window (Process: explorer.exe)"]

    # Prepare the WHERE clause for the query using LIKE for each window title
    query = "DELETE FROM activity_logs WHERE "
    conditions = []
    for title in window_titles_to_remove:
        conditions.append("window_title LIKE ?")
    
    # Join the conditions with OR
    query += " OR ".join(conditions)

    # Execute the DELETE query
    cursor.execute(query, tuple(f"%{title}%" for title in window_titles_to_remove))

    conn.commit()
    conn.close()
    print(f"Logs with specified titles have been removed.")

# **Categorize Activities**
def categorize_data():
    conn = sqlite3.connect('time_tracking.db')
    cursor = conn.cursor()

    # Define refined keyword-to-category mappings
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

    # Fetch all uncategorized logs
    cursor.execute('''
    SELECT id, window_title FROM activity_logs WHERE category IS NULL
    ''')
    logs = cursor.fetchall()
    print("Uncategorized Logs:")
    print(logs)

    # Update categories based on keywords
    for log_id, window_title in logs:
        category = None
        for keyword, mapped_category in keyword_to_category.items():
            if keyword.lower() in window_title.lower():
                category = mapped_category
                break  # Stop at the first match
        if category is None:
            category = 'Other'  # Default to 'Other' if no category matches
        
        # Update category in the database
        cursor.execute('''
        UPDATE activity_logs
        SET category = ?
        WHERE id = ?
        ''', (category, log_id))

    conn.commit()
    remove_specific_logs()

    # Now fetch and print all logs that were categorized as 'Other'
    cursor.execute('''
    SELECT id, window_title FROM activity_logs WHERE category = 'Other'
    ''')

    other_logs = cursor.fetchall()
    print("\nLogs categorized as 'Other':")
    for log in other_logs:
        print(log)

    conn.close()
    print("Categorization complete.")
