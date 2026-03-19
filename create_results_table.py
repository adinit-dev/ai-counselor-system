import sqlite3

conn = sqlite3.connect("database/mental_health.db")
cursor = conn.cursor()

# RESULTS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    test_id INTEGER,
    score INTEGER,
    risk TEXT
)
""")

# 🔥 ADD THIS (VERY IMPORTANT)
cursor.execute("""
CREATE TABLE IF NOT EXISTS responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    test_id INTEGER,
    question_id INTEGER,
    answer TEXT
)
""")

conn.commit()
conn.close()

print("Results + Responses tables created successfully")