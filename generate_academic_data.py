import sqlite3
from faker import Faker
import random

fake = Faker()

conn = sqlite3.connect("database/mental_health.db")
cursor = conn.cursor()

# subjects list
subjects = [
    "Data Structures",
    "Operating Systems",
    "Computer Networks",
    "Database Systems",
    "Algorithms"
]

# get all students
cursor.execute("SELECT id FROM students")
students = cursor.fetchall()

for student in students:

    student_id = student[0]

    for subject in subjects:

        # -------- MARKS --------

        a1 = random.randint(0,5)
        a2 = random.randint(0,5)
        a3 = random.randint(0,5)
        a4 = random.randint(0,5)

        mid = random.randint(10,30)
        end = random.randint(20,50)

        total = a1 + a2 + a3 + a4 + mid + end

        cursor.execute("""
        INSERT INTO marks(
        student_id,subject,
        assessment1,assessment2,midsem,
        assessment3,assessment4,endsem,total
        )
        VALUES (?,?,?,?,?,?,?,?,?)
        """,(student_id,subject,a1,a2,mid,a3,a4,end,total))


        # -------- ATTENDANCE --------

        total_classes = random.randint(35,50)
        attended = random.randint(20,total_classes)

        percentage = round((attended/total_classes)*100,2)

        cursor.execute("""
        INSERT INTO attendance(
        student_id,subject,total_classes,attended_classes,percentage
        )
        VALUES (?,?,?,?,?)
        """,(student_id,subject,total_classes,attended,percentage))


conn.commit()
conn.close()

print("Academic data generated")