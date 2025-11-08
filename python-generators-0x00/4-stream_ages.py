#!/usr/bin/env python3
"""
Memory-efficient average age using generators.
Streams ages one-by-one from DB, computes without full load.
"""

import seed
from mysql.connector import Error
import sys

def stream_user_ages():
    """Generator that streams user ages from the database."""
    conn = None
    cursor = None
    try:
        conn = seed.connect_to_prodev()
        if not conn or not conn.is_connected():
            raise Error("Failed to connect to ALX_prodev database.")

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT age FROM user_data")

        for row in cursor:  # Loop 1
            yield row['age']
    except Error as e:
        print(f"Error streaming ages: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def average_age():
    """Calculate the average age of users from the streamed ages."""
    total_age = 0.0
    count = 0
    for age in stream_user_ages():  # Loop 2
        total_age += age
        count += 1
    if count == 0:
        avg = 0
    else:
        avg = total_age / count
    print(f"Average age of users: {avg}")

if __name__ == "__main__":
    try:
        average_age()
    except BrokenPipeError:
        sys.stderr.close()
