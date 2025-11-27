import sqlite3
import functools
from datetime import datetime

# Quick DB setup (run once)
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)')
    cursor.executemany('INSERT OR IGNORE INTO users (name) VALUES (?)', [('Alice',), ('Bob',)])
    conn.commit()
    conn.close()

init_db()

def log_queries(func):
    """Safe decorator to log SQL queries to query.log"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Safely get the query
        query = kwargs.get('query') or (args[0] if args else None)
        if not isinstance(query, str):
            query = '<no valid SQL query provided>'

        # Timestamp for the log
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {func.__name__}: {query}\n"

        # Log to file and console
        with open('query.log', 'a') as log_file:
            log_file.write(log_entry)
        print(log_entry.strip())

        # Execute wrapped function
        return func(*args, **kwargs)
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# Run demo
users = fetch_all_users(query="SELECT * FROM users")
print(f"Fetched {len(users)} users: {users}")
