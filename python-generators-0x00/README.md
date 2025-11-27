# Seed MySQL Database Script

## Overview

This Python script (`seed.py`) automates the setup and population of a MySQL database named `ALX_prodev`. It creates the database (if it doesn't exist), connects to it, creates a `user_data` table with specified fields, and inserts sample data from a CSV file (`user_data.csv`). The script uses UUIDs for primary keys to ensure uniqueness and handles duplicate email insertions gracefully.

### Key Features
- **Database Creation**: Creates `ALX_prodev` database on a MySQL server.
- **Table Schema**: Creates `user_data` table with:
  - `user_id`: CHAR(36) PRIMARY KEY (UUID, indexed by default).
  - `name`: VARCHAR(255) NOT NULL.
  - `email`: VARCHAR(255) NOT NULL UNIQUE.
  - `age`: DECIMAL(5,2) NOT NULL.
- **Data Seeding**: Reads from `user_data.csv` (columns: `name`, `email`, `age`) and inserts rows, skipping duplicates based on email.
- **Error Handling**: Logs connection issues, duplicates, and CSV errors.
- **Environment-Driven**: Uses `.env` file for MySQL credentials via `python-dotenv`.

## Prerequisites

- Python 3.8+.
- MySQL server (version 8.0+ recommended) running and accessible.
- Required Python packages:
  - `mysql-connector-python` (for MySQL interaction).
  - `python-dotenv` (for loading environment variables).
  - `csv` and `uuid` (built-in, no install needed).

Install dependencies:
```bash
pip install mysql-connector-python python-dotenv
```

- A `user_data.csv` file in the same directory as `seed.py` with the following format (no header row assumed for simplicity; adjust if needed):
  ```
  John Doe,john@example.com,25.5
  Jane Smith,jane@example.com,30.0
  Bob Johnson,bob@example.com,45.75
  ```

## Setup

1. **Clone or Download**: Place `seed.py` in your project directory.
2. **Create `.env` File**: Add your MySQL credentials:
   ```
   MYSQL_HOST=localhost
   MYSQL_USER=your_username
   MYSQL_PASSWORD=your_password
   MYSQL_PORT=3306
   ```
   **Security Note**: Never commit `.env` to version control. Add it to `.gitignore`.

3. **Prepare CSV**: Ensure `user_data.csv` exists with sample data (as shown above). The script uses `csv.DictReader`, so include a header row if your CSV has one (e.g., `name,email,age`).

## Usage

Run the script from the command line:
```bash
python seed.py
```

### Expected Output
```
Successfully connected to MySQL server.
Database ALX_prodev created or already exists.
Successfully connected to ALX_prodev database.
Table user_data created or already exists.
Inserted data for john@example.com.
Inserted data for jane@example.com.
Inserted data for bob@example.com.
Seeding completed.
```

- If a row's email already exists, it skips with: `Data for {email} already exists.`
- If `user_data.csv` is missing: `user_data.csv file not found.`

### Script Flow
1. Connects to MySQL server (no DB specified).
2. Creates `ALX_prodev` database.
3. Connects to `ALX_prodev`.
4. Creates `user_data` table.
5. Reads CSV rows and inserts each (generating UUID for `user_id`).

## Functions

- `connect_db()`: Establishes connection to MySQL server using env vars.
- `create_database(connection)`: Creates `ALX_prodev` if missing.
- `connect_to_prodev()`: Connects specifically to `ALX_prodev`.
- `create_table(connection)`: Creates `user_data` table if missing.
- `insert_data(connection, data)`: Inserts a single row dict from CSV, handling duplicates.

## Troubleshooting

- **Connection Errors**: Verify MySQL server is running and credentials in `.env` are correct. Check firewall/port.
- **CSV Issues**: Ensure UTF-8 encoding; no extra quotes/escapes in data. If header present, `DictReader` will use it.
- **Duplicate Emails**: Script skips them (due to UNIQUE constraint on email).
- **UUID Length**: `CHAR(36)` fits standard UUID strings.
- **Permissions**: MySQL user needs `CREATE DATABASE`, `CREATE TABLE`, and `INSERT` privileges.
- **Logs**: All errors print to console; add logging module for production.

## License

## Contributing

Issues welcome!

---

*Generated on November 08, 2025*
