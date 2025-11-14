import sqlite3

# Optional: Initialize the database with sample data including 'age' column (run once)
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            age INTEGER
        )
    ''')
    # Insert sample data with ages
    cursor.executemany(
        'INSERT OR IGNORE INTO users (name, email, age) VALUES (?, ?, ?)',
        [
            ('Alice', 'alice@example.com', 30),
            ('Bob', 'bob@example.com', 20),
            ('Charlie', 'charlie@example.com', 26)
        ]
    )
    conn.commit()
    conn.close()

init_db()  # Initialize if needed

class ExecuteQuery:
    def __init__(self, query: str, params: tuple = ()):
        self.query = query
        self.params = params
        self.conn = None
        self.cursor = None
        self.results = None

    def __enter__(self):
        self.conn = sqlite3.connect('users.db')
        self.conn.isolation_level = 'DEFERRED'  # Enable transactions
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.query, self.params)
        self.results = self.cursor.fetchall()
        return self.results

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            if exc_type:
                self.conn.rollback()
            else:
                self.conn.commit()
            self.conn.close()
        return False  # Do not suppress exceptions

# Usage: Execute the query and get results
with ExecuteQuery("SELECT * FROM users WHERE age > ?", (25,)) as results:
    print(results)  # Output: [(1, 'Alice', 'alice@example.com', 30), (3, 'Charlie', 'charlie@example.com', 26)]
