import sqlite3
import threading
from datetime import datetime

# Global database connection lock
db_lock = threading.Lock()

def get_db_connection():
    """Create a new database connection for the current thread"""
    conn = sqlite3.connect('time_tracking.db')
    conn.row_factory = sqlite3.Row
    return conn

def setup_database():
    """Initialize the database and create/update tables"""
    try:
        with get_db_connection() as conn:
            # Check if we need to migrate the database
            cursor = conn.cursor()
            
            # Check if activity_logs table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='activity_logs'
            """)
            
            if cursor.fetchone() is None:
                # Create new table
                cursor.execute('''
                    CREATE TABLE activity_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT DEFAULT (datetime('now')),
                        window_title TEXT,
                        process_name TEXT,
                        category TEXT,
                        time_spent REAL
                    )
                ''')
            else:
                # Check if process_name column exists
                cursor.execute("PRAGMA table_info(activity_logs)")
                columns = [column[1] for column in cursor.fetchall()]
                
                if 'process_name' not in columns:
                    # Add process_name column if it doesn't exist
                    cursor.execute('''
                        ALTER TABLE activity_logs
                        ADD COLUMN process_name TEXT
                    ''')

            # Create categories table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    keyword TEXT,
                    category TEXT
                )
            ''')
            
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database setup error: {e}")
        raise

def record_window_activity(window_title, process_name, time_spent):
    """Record window activity with thread-safe database access"""
    try:
        with db_lock:
            conn = get_db_connection()
            with conn:
                conn.execute('''
                    INSERT INTO activity_logs (timestamp, window_title, process_name, time_spent, category)
                    VALUES (?, ?, ?, ?, NULL)
                ''', (datetime.now(), window_title, process_name, time_spent))
    except sqlite3.Error as e:
        print(f"Error logging window time: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

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
        "League of Legends": "League of Legends",
        "Ζωγραφική": "Paint",
        "Folder": "Folder"
    }

    with sqlite3.connect('time_tracking.db') as conn:
        cursor = conn.cursor()

        # Remove specific logs
        remove_specific_logs(cursor, window_titles_to_remove)

        # Fetch all uncategorized logs
        cursor.execute('SELECT id, window_title FROM activity_logs WHERE category IS NULL')
        logs = cursor.fetchall()

        # Update categories based on keywords
        for log_id, window_title in logs:
            category = next(
                (mapped_category for keyword, mapped_category in keyword_to_category.items()
                 if keyword.lower() in window_title.lower()), "Other"  # Default to 'Other' if no category matches
            )
            cursor.execute('UPDATE activity_logs SET category = ? WHERE id = ?', (category, log_id))

        conn.commit()

        # TODO: Remove it because a graph is created to show 'other' categories.
        # Fetch and print logs categorized as 'Other'
        cursor.execute('SELECT id, window_title FROM activity_logs WHERE category = "Other"')
        other_logs = cursor.fetchall()
        print("\nLogs categorized as 'Other':", other_logs)

def fetch_time_by_category_for_date(date):
    query = '''
        SELECT category, SUM(time_spent) 
        FROM activity_logs 
        WHERE date(timestamp) = ? 
        GROUP BY category
    '''
    with sqlite3.connect('time_tracking.db') as conn:
        return conn.execute(query, (date,)).fetchall()

def fetch_time_by_category_for_week(start_date, end_date):
    query = '''
        SELECT category, SUM(time_spent) 
        FROM activity_logs 
        WHERE date(timestamp) BETWEEN ? AND ? 
        GROUP BY category
    '''
    with sqlite3.connect('time_tracking.db') as conn:
        return conn.execute(query, (start_date, end_date)).fetchall()
