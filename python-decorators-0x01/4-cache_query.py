import time
import sqlite3
import functools
import json

CACHE_TTL = 10  # Time-to-live for cached result in seconds
CACHE_FILE = "query_cache.json"

# Load cache from file at startup
try:
    with open(CACHE_FILE, "r") as f:
        query_cache = json.load(f)  # {"query": [timestamp, result_as_list]}
except (FileNotFoundError, json.JSONDecodeError):
    query_cache = {}

def save_cache():
    """Saves the updated cache to the file for persistence"""
    with open(CACHE_FILE, "w") as f:
        json.dump(query_cache, f, indent=4)

def cache_query(func):
    """A decorator that caches the results of database queries"""
    @functools.wraps(func)
    def wrapper(conn, query, *args, **kwargs):
        now = time.time()
        if query in query_cache:
            timestamp, cached_result = query_cache[query]
            if now - timestamp < CACHE_TTL:
                return cached_result  # Assume list of lists/dicts
        result = func(conn, query, *args, **kwargs)
        # Serialize as list of lists for JSON
        serial_result = [list(row) for row in result]  # Tuples → lists
        query_cache[query] = (now, serial_result)
        save_cache()
        return result  # Return original tuples
    return wrapper

def with_db_connection(func):
    """A decorator that automatically handles opening and closing database connections"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect("users.db")
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")

first_user = fetch_users_with_cache(query="SELECT * FROM users WHERE id=1")
