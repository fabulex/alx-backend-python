import sqlite3

# Optional: Initialize the database with sample data (run once)
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')
    cursor.executemany('INSERT OR IGNORE INTO users (name) VALUES (?)', [('Alice',), ('Bob',)])
    conn.commit()
    conn.close()

init_db()  # Initialize if needed

class DatabaseConnection:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.conn = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.conn.isolation_level = 'DEFERRED'  # Enable transactions
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if exc_type:
                self.conn.rollback()
            else:
                self.conn.commit()
            self.conn.close()
        return False  # Do not suppress exceptions

# Usage with 'with' statement to query and print results
with DatabaseConnection('users.db') as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
    print(results)
