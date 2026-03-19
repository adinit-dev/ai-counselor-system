from faker import Faker
import sqlite3

fake = Faker()

conn = sqlite3.connect("database/mental_health.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM students")

for i in range(20):

    name = fake.name()
    email = name.lower().replace(" ", ".") + "@nitap.ac.in"
    password = "1234"

    cursor.execute(
        "INSERT INTO students(name,email,password) VALUES (?,?,?)",
        (name,email,password)
    )

conn.commit()
conn.close()

print("Fake students created")