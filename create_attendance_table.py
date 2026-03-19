import sqlite3

conn = sqlite3.connect("database/mental_health.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance(
id INTEGER PRIMARY KEY AUTOINCREMENT,
student_id INTEGER,
subject TEXT,
total_classes INTEGER,
attended_classes INTEGER,
percentage REAL
)
""")

conn.commit()
conn.close()

print("Attendance table created")