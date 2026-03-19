import sqlite3

conn = sqlite3.connect("database/mental_health.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS marks(
id INTEGER PRIMARY KEY AUTOINCREMENT,
student_id INTEGER,
subject TEXT,
assessment1 INTEGER,
assessment2 INTEGER,
midsem INTEGER,
assessment3 INTEGER,
assessment4 INTEGER,
endsem INTEGER,
total INTEGER
)
""")

conn.commit()
conn.close()

print("Marks table created")