import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "database", "mental_health.db")

DB_PATH = os.path.abspath(DB_PATH)

# ensure database folder exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ---------------- STUDENTS ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS students(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
email TEXT,
password TEXT
)
""")

# ---------------- COUNSELORS ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS counselors(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
email TEXT,
password TEXT
)
""")

# ---------------- TESTS ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS tests(
id TEXT PRIMARY KEY,
test_name TEXT
)
""")
# ---------------- QUESTIONS ----------------

cursor.execute("""
CREATE TABLE questions(
id INTEGER PRIMARY KEY AUTOINCREMENT,
test_id TEXT,
question_text TEXT,
option1 TEXT,
option2 TEXT,
option3 TEXT,
option4 TEXT
)
""")

cursor.execute("""
INSERT INTO counselors (name,email,password)
VALUES (?,?,?)
""",(
"Head Counselor",
"counselor@college.edu",
"admin123"
))


# ---------------- RESPONSES ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS responses(
id INTEGER PRIMARY KEY AUTOINCREMENT,
student_id INTEGER,
test_id INTEGER,
question_id INTEGER,
answer TEXT
)
""")

conn.commit()
conn.close()

print("Database tables created successfully")