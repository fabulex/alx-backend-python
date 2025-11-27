#!/usr/bin/env python3
"""
Stream users from the database using a generator.
Reuses seed.py for connection modularity, with robust error handling and dict output.
"""

import seed  # Assumes seed.py is in the same directory or Python path
from mysql.connector import Error

def stream_users():
    """
    Generator function that streams rows from the user_data table one by one.

    Yields each row as a dict: {'user_id': str, 'name': str, 'email': str, 'age': int}
    Handles connection errors and ensures cleanup.
    """
    conn = None
    cursor = None
    try:
        conn = seed.connect_to_prodev()
        if not conn or not conn.is_connected():
            raise Error("Failed to connect to ALX_prodev database.")

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data")

        for row in cursor:
            yield {
                'user_id': row['user_id'],
                'name': row['name'],
                'email': row['email'],
                'age': int(row['age'])
            }
    except Error as e:
        print(f"Error streaming users: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
