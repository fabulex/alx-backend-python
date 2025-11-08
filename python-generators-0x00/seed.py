import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import csv
import uuid

# Load environment variables from .env file
load_dotenv()

def connect_db():
    """Connects to the MySQL database server."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            port=int(os.getenv('MYSQL_PORT', 3306))
        )
        if connection.is_connected():
            print("Successfully connected to MySQL server.")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def create_database(connection):
    """Creates the database ALX_prodev if it does not exist."""
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        print("Database ALX_prodev created or already exists.")
        cursor.close()
    except Error as e:
        print(f"Error creating database: {e}")

def connect_to_prodev():
    """Connects to the ALX_prodev database in MySQL."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            database='ALX_prodev',
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            port=int(os.getenv('MYSQL_PORT', 3306))
        )
        if connection.is_connected():
            print("Successfully connected to ALX_prodev database.")
            return connection
    except Error as e:
        print(f"Error connecting to ALX_prodev: {e}")
        return None

def create_table(connection):
    """Creates the table user_data if it does not exist with the required fields."""
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                user_id CHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                age DECIMAL(5,2) NOT NULL
            )
        """)
        print("Table user_data created or already exists.")
        cursor.close()
    except Error as e:
        print(f"Error creating table: {e}")

def insert_data(connection, data):
    """Inserts data into the database if it does not exist."""
    cursor = connection.cursor()
    user_id = str(uuid.uuid4())
    try:
        cursor.execute("""
            INSERT INTO user_data (user_id, name, email, age)
            VALUES (%s, %s, %s, %s)
        """, (user_id, data['name'], data['email'], float(data['age'])))
        connection.commit()
        print(f"Inserted data for {data['email']}.")
    except Error as e:
        if "Duplicate entry" in str(e):
            print(f"Data for {data['email']} already exists.")
        else:
            print(f"Error inserting data for {data['email']}: {e}")
    finally:
        cursor.close()

if __name__ == "__main__":
    # Step 1: Connect to MySQL server and create database
    conn = connect_db()
    if conn:
        create_database(conn)
        conn.close()

    # Step 2: Connect to ALX_prodev and create table
    prodev_conn = connect_to_prodev()
    if prodev_conn:
        create_table(prodev_conn)

        # Step 3: Read CSV and insert data
        try:
            with open('user_data.csv', 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    insert_data(prodev_conn, row)
        except FileNotFoundError:
            print("user_data.csv file not found.")
        except Exception as e:
            print(f"Error reading CSV: {e}")
        finally:
            prodev_conn.close()
        print("Seeding completed.")
