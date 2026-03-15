import sqlite3

conn = sqlite3.connect("database/mental_health.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM responses")

conn.commit()
conn.close()

print("Responses table cleared.")