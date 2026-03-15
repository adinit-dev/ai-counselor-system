import sqlite3

conn = sqlite3.connect("database/mental_health.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    test_id TEXT,
    score INTEGER,
    risk TEXT
)
""")

conn.commit()
conn.close()

print("Results table created successfully")