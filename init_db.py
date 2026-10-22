import sqlite3
import os

DB_FILE = "database.db"
SEED_FILE = "seed-data.sql"

def init_db():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Removed old {DB_FILE}")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    with open(SEED_FILE, "r") as f:
        sql_script = f.read()

    cursor.executescript(sql_script)
    conn.commit()
    conn.close()
    print("Database initialized successfully with seed data.")

if __name__ == "__main__":
    init_db()