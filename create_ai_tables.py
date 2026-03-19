import sqlite3

conn = sqlite3.connect("database/mental_health.db")
cursor = conn.cursor()

# ---------- ATTENDANCE LOG ----------
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance_log(
id INTEGER PRIMARY KEY AUTOINCREMENT,
student_id INTEGER,
subject TEXT,
date TEXT,
status TEXT
)
""")

# ---------- QUESTIONS TABLE ----------
cursor.execute("""
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id INTEGER,
    question_text TEXT,
    option1 TEXT,
    option2 TEXT,
    option3 TEXT,
    option4 TEXT
)
""")

# ---------- EXAM RESULTS ----------
cursor.execute("""
CREATE TABLE IF NOT EXISTS exam_results(
id INTEGER PRIMARY KEY AUTOINCREMENT,
student_id INTEGER,
subject TEXT,
exam_type TEXT,
marks INTEGER,
max_marks INTEGER,
date TEXT
)
""")

conn.commit()
conn.close()

print("AI-ready tables created")