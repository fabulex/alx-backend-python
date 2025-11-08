#!/usr/bin/env python3
"""
Lazy pagination generator for users from the database.
Fetches pages on-demand using secure OFFSET and LIMIT.
"""

import seed
from mysql.connector import Error

def paginate_users(page_size, offset):
    """Fetch a page of user data from the database securely."""
    conn = None
    cursor = None
    try:
        conn = seed.connect_to_prodev()
        if not conn or not conn.is_connected():
            raise Error("Failed to connect to ALX_prodev database.")

        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM user_data LIMIT %s OFFSET %s",
            (page_size, offset)
        )
        rows = cursor.fetchall()
        # Convert to dicts with int age
        users = [{
            'user_id': row['user_id'],
            'name': row['name'],
            'email': row['email'],
            'age': int(row['age'])
        } for row in rows]
        return users
    except Error as e:
        print(f"Error paginating users: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def lazy_paginate(page_size):
    """Generator that simulates lazy pagination of user data."""
    offset = 0
    # Infinite loop to fetch pages until no more data is available
    while True:
        # Fetch a page of user data
        page = paginate_users(page_size, offset)
        # If the generator returns an empty page, break the loop
        if not page:
            break
        # Update the offset for the next page
        offset += page_size
        yield page
