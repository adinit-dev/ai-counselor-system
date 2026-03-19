import sqlite3
import random
from datetime import datetime, timedelta

conn = sqlite3.connect("database/mental_health.db")
cursor = conn.cursor()

subjects = [
    "Data Structures",
    "Operating Systems",
    "Computer Networks",
    "Database Systems",
    "Algorithms"
]

# get students
cursor.execute("SELECT id FROM students")
students = cursor.fetchall()

start_date = datetime(2026,1,1)

# ---------- ATTENDANCE GENERATION ----------
for student in students:

    student_id = student[0]

    for subject in subjects:

        for day in range(60):   # 2 months of classes

            date = start_date + timedelta(days=day)

            # 80% probability of present
            status = "present" if random.random() < 0.8 else "absent"

            cursor.execute("""
            INSERT INTO attendance_log(student_id,subject,date,status)
            VALUES (?,?,?,?)
            """,(student_id,subject,date.strftime("%Y-%m-%d"),status))


# ---------- EXAM RESULTS ----------
exam_structure = [
("A1",5),
("A2",5),
("MID",30),
("A3",5),
("A4",5),
("END",50)
]

for student in students:

    student_id = student[0]

    for subject in subjects:

        for exam,max_marks in exam_structure:

            marks = random.randint(int(max_marks*0.4),max_marks)

            cursor.execute("""
            INSERT INTO exam_results(student_id,subject,exam_type,marks,max_marks,date)
            VALUES (?,?,?,?,?,?)
            """,(
                student_id,
                subject,
                exam,
                marks,
                max_marks,
                datetime.now().strftime("%Y-%m-%d")
            ))

conn.commit()
conn.close()

print("AI dataset generated")