from faker import Faker
import sqlite3

fake = Faker()

conn = sqlite3.connect("database/mental_health.db")
cursor = conn.cursor()

for i in range(20):

    name = fake.name()
    email = fake.email()
    password = "1234"

    cursor.execute(
        "INSERT INTO students(name,email,password) VALUES (?,?,?)",
        (name,email,password)
    )

conn.commit()
conn.close()

print("Fake students created")