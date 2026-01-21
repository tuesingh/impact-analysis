import sqlite3
from pathlib import Path

DB_FILE = str(Path(__file__).parent.parent / "compliance.db")

def get_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    return conn

def initialize_db():
    conn = get_connection()
    cur = conn.cursor()
    # Regulations table
    cur.execute("""CREATE TABLE IF NOT EXISTS regulations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        date TEXT,
        regulator TEXT,
        impact TEXT,
        body TEXT,
        status TEXT
    )""")
    # Policies table
    cur.execute("""CREATE TABLE IF NOT EXISTS policies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        impacted_by TEXT,
        review_status TEXT
    )""")
    # Tasks table
    cur.execute("""CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT,
        policy TEXT,
        assigned_to TEXT,
        status TEXT
    )""")
    conn.commit()
    conn.close()

def insert_regulation(reg):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO regulations (title, date, regulator, impact, body, status) VALUES (?, ?, ?, ?, ?, ?)",
        (reg["title"], reg["date"], reg["regulator"], reg["impact"], reg["body"], reg["status"])
    )
    conn.commit()
    conn.close()

def get_all_regulations():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM regulations")
    rows = cur.fetchall()
    conn.close()
    return [
        {"id": row[0], "title": row[1], "date": row[2], "regulator": row[3], "impact": row[4], "body": row[5], "status": row[6]}
        for row in rows
    ]

def insert_policy(pol):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO policies (name, description, impacted_by, review_status) VALUES (?, ?, ?, ?)",
        (pol["name"], pol["description"], pol["impacted_by"], pol["review_status"])
    )
    conn.commit()
    conn.close()

def get_all_policies():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM policies")
    rows = cur.fetchall()
    conn.close()
    return [
        {"id": row[0], "name": row[1], "description": row[2], "impacted_by": row[3], "review_status": row[4]}
        for row in rows
    ]

def insert_task(task):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (task, policy, assigned_to, status) VALUES (?, ?, ?, ?)",
        (task["task"], task["policy"], task["assigned_to"], task["status"])
    )
    conn.commit()
    conn.close()

def get_all_tasks():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks")
    rows = cur.fetchall()
    conn.close()
    return [
        {"id": row[0], "task": row[1], "policy": row[2], "assigned_to": row[3], "status": row[4]}
        for row in rows
    ]

def clear_all():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM regulations")
    cur.execute("DELETE FROM policies")
    cur.execute("DELETE FROM tasks")
    conn.commit()
    conn.close()
