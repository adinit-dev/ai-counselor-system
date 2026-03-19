import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "mental_health.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS counselors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    password TEXT
)
""")

# clear old duplicates (optional but safe)
cursor.execute("DELETE FROM counselors")

cursor.execute("""
INSERT INTO counselors (email, password)
VALUES (?, ?)
""", ("counselor@college.edu", "admin123"))

conn.commit()
conn.close()

print("✅ Counselor table created in correct DB")