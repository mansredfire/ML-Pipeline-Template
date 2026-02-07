# Database Guide

How to use SQL databases with ML Pipeline Template.

---

## Overview

ML Pipeline Template can store and train on data from any SQL database. SQLite works right away with no setup. PostgreSQL and MySQL need one extra install. The pipeline is **database-agnostic** — just change the connection string and everything else works the same.

---

## Supported Databases

| Database | Extra Install Needed | Best For |
|---|---|---|
| **SQLite** | None (already built in) | Learning, testing, small projects |
| **PostgreSQL** | `pip install psycopg2-binary` | Large datasets, production apps |
| **MySQL** | `pip install pymysql` | Web apps, shared hosting |
| **SQL Server** | `pip install pyodbc` | Enterprise, Windows environments |

---

## Connection Strings

These tell the pipeline which database to connect to:

```
sqlite:///data/stock_events.db
postgresql://user:password@localhost:5432/mydb
mysql://user:password@localhost:3306/mydb
mssql+pyodbc://user:password@host/mydb?driver=ODBC+Driver+17+for+SQL+Server
```

**SQLite path notes:**
- Relative: `sqlite:///data/stock_events.db`
- Absolute (Windows): `sqlite:///C:/Users/me/project/data/stock_events.db`
- Absolute (Linux/Mac): `sqlite:////home/me/project/data/stock_events.db` (four slashes)

**Special characters in passwords** — URL-encode them:

| Character | Encoded |
|---|---|
| `@` | `%40` |
| `:` | `%3A` |
| `/` | `%2F` |
| `#` | `%23` |

---

## Database Table Layout

Your table columns should match the fields the pipeline expects. Here's what each column means:

### Required Columns

| Column | Type | What It Is | Example |
|---|---|---|---|
| `report_id` | TEXT/VARCHAR | Unique ID for each record | "EVT-001" |
| `target_domain` | TEXT/VARCHAR | Stock ticker | "AAPL" |
| `target_company` | TEXT/VARCHAR | Company name | "Apple" |
| `record_type` | TEXT/VARCHAR | Event type | "Stock Goes Up" |
| `severity` | TEXT/VARCHAR | How serious it is | "high" |
| `priority_score` | REAL/FLOAT | Impact score (0–10) | 7.5 |

### Optional Columns (help the model be more accurate)

| Column | Type | What It Is |
|---|---|---|
| `technology_stack` | TEXT | Data sources used (comma-separated) |
| `description` | TEXT | Plain-English description of the event |
| `endpoint` | TEXT/VARCHAR | API endpoint where data came from |
| `http_method` | TEXT/VARCHAR | How data was fetched (GET/POST) |
| `reward_amount` | REAL/FLOAT | Estimated price impact in dollars |
| `authentication_required` | BOOLEAN | Does the data source need a login? |
| `complexity` | TEXT/VARCHAR | low/medium/high |
| `created_date` | DATE | When the event happened |
| `source_quality` | INTEGER | How reliable the source is (higher = better) |

### Example: Create the Table

```sql
CREATE TABLE stock_events (
    report_id VARCHAR(255) PRIMARY KEY,
    target_domain VARCHAR(255) NOT NULL,
    target_company VARCHAR(255) NOT NULL,
    record_type VARCHAR(255) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    priority_score FLOAT NOT NULL,
    technology_stack TEXT,
    description TEXT,
    endpoint VARCHAR(500),
    http_method VARCHAR(10),
    reward_amount FLOAT,
    authentication_required BOOLEAN,
    complexity VARCHAR(50),
    created_date DATE,
    source_quality INTEGER
);
```

---

## SQLite Setup

No installation needed — SQLite comes with Python.

### Create a Database

```python
import sqlite3

conn = sqlite3.connect('data/stock_events.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE stock_events (
        report_id TEXT PRIMARY KEY,
        target_domain TEXT NOT NULL,
        target_company TEXT NOT NULL,
        record_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        priority_score REAL NOT NULL,
        technology_stack TEXT,
        description TEXT,
        endpoint TEXT,
        http_method TEXT,
        reward_amount REAL
    )
''')

conn.commit()
conn.close()
```

### Try It Without a Database First

You don't need a database to get started. The mock data generator creates everything in memory:

```bash
python scripts/train_with_mock_data.py --reports 1000
```

---

## PostgreSQL Setup

### Install
- **Windows**: Download from [postgresql.org](https://www.postgresql.org/download/windows/)
- **Linux**: `sudo apt install postgresql postgresql-contrib -y`
- **macOS**: `brew install postgresql`

### Python Package
```bash
pip install psycopg2-binary
```

### Create Database
```sql
CREATE DATABASE stockdata;
CREATE USER mluser WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE stockdata TO mluser;
```

### Connection String
```
postgresql://mluser:yourpassword@localhost:5432/stockdata
```

---

## MySQL Setup

### Install
- **Windows**: Download from [mysql.com](https://dev.mysql.com/downloads/installer/)
- **Linux**: `sudo apt install mysql-server -y`
- **macOS**: `brew install mysql`

### Python Package
```bash
pip install pymysql
```

### Create Database
```sql
CREATE DATABASE stockdata;
CREATE USER 'mluser'@'localhost' IDENTIFIED BY 'yourpassword';
GRANT ALL PRIVILEGES ON stockdata.* TO 'mluser'@'localhost';
FLUSH PRIVILEGES;
```

### Connection String
```
mysql://mluser:yourpassword@localhost:3306/stockdata
```

---

## SQL Server Setup

### Install
- Download [SQL Server Express](https://www.microsoft.com/en-us/sql-server/sql-server-downloads)
- Install [ODBC Driver 17 for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

### Python Package
```bash
pip install pyodbc
```

### Connection String
```
mssql+pyodbc://mluser:yourpassword@localhost/stockdata?driver=ODBC+Driver+17+for+SQL+Server
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `No module named 'psycopg2'` | Run `pip install psycopg2-binary` |
| `No module named 'pymysql'` | Run `pip install pymysql` |
| `No module named 'pyodbc'` | Run `pip install pyodbc` |
| "unable to open database file" (SQLite) | Make sure the `data/` folder exists: `mkdir -p data` |
| "database is locked" (SQLite) | Close other programs using the file |
| "password authentication failed" | Double-check your username and password |
| "could not connect to server" | Make sure the database server is running |
| Connection timeout | Check firewall settings and that the port is open |

---

## Quick Reference

```bash
# SQLite (no setup needed)
sqlite:///data/stock_events.db

# PostgreSQL
postgresql://user:pass@localhost:5432/stockdata

# MySQL
mysql://user:pass@localhost:3306/stockdata

# SQL Server
mssql+pyodbc://user:pass@localhost/stockdata?driver=ODBC+Driver+17+for+SQL+Server
```
