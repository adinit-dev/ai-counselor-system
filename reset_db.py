import sqlite3
import os

DB_PATH = "database/mental_health.db"

# DELETE OLD DB
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("🗑 Old DB deleted")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# =====================
# TABLES
# =====================

# STUDENTS
cursor.execute("""
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    password INTEGER
)
""")

# TESTS
cursor.execute("""
CREATE TABLE tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT
)
""")

# RESULTS (IMPORTANT)
cursor.execute("""
CREATE TABLE results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    test_id INTEGER,
    score INTEGER,
    risk TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# =====================
# SEED CLEAN TESTS
# =====================

tests = [
    ("Student Stress Assessment",),
    ("Sleep & Wellbeing Assessment",),
    ("Anxiety Detection Test",),
]

cursor.executemany("INSERT INTO tests (title) VALUES (?)", tests)

conn.commit()
conn.close()

print("✅ Fresh DB ready")