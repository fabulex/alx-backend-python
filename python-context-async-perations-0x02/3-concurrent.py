import asyncio
import aiosqlite
import sqlite3  # For initial DB setup

# Initialize the database with sample data (run once)
DB_PATH = 'users.db'

def init_db():
    """Initialize the database with a users table and sample data including ages."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER
        )
    ''')
    # Insert sample data with varying ages
    cursor.executemany(
        'INSERT OR IGNORE INTO users (name, age) VALUES (?, ?)',
        [
            ('Alice', 25),
            ('Bob', 45),
            ('Charlie', 30),
            ('Diana', 50),
            ('Eve', 35)
        ]
    )
    conn.commit()
    conn.close()

init_db()  # Run once to set up the DB

async def async_fetch_users():
    """Fetch all users asynchronously."""
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row  # Dict-like rows
        async with conn.execute('SELECT * FROM users') as cursor:
            return await cursor.fetchall()

async def async_fetch_older_users():
    """Fetch users older than 40 asynchronously."""
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute('SELECT * FROM users WHERE age > 40') as cursor:
            return await cursor.fetchall()

async def fetch_concurrently():
    """Execute both queries concurrently using asyncio.gather."""
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users(),
        return_exceptions=True  # Handle isolated errors
    )
    print("All users:", [dict(u) for u in all_users])
    print("Users older than 40:", [dict(u) for u in older_users])
    return all_users, older_users

# Run the concurrent fetch
if __name__ == "__main__":
    asyncio.run(fetch_concurrently())
