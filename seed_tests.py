import sqlite3

conn = sqlite3.connect("database/mental_health.db")
cursor = conn.cursor()

# ---------- TEST 1 ----------
cursor.execute(
"INSERT INTO tests(title) VALUES (?)",
("Student Stress Assessment",)
)

stress_test_id = cursor.lastrowid

stress_questions = [
"How often do you feel overwhelmed by academic workload?",
"How often do you feel anxious before exams?",
"How often do you struggle to concentrate while studying?",
"How often do you feel pressure to meet academic expectations?",
"How often do you feel mentally exhausted after classes?"
]

for q in stress_questions:
    cursor.execute("""
    INSERT INTO questions
    (test_id,question_text,option1,option2,option3,option4)
    VALUES (?,?,?,?,?,?)
    """,(
        stress_test_id,
        q,
        "Never",
        "Sometimes",
        "Often",
        "Always"
    ))

# ---------- TEST 2 ----------
cursor.execute(
"INSERT INTO tests(title) VALUES (?)",
("Sleep & Wellbeing Assessment",)
)

sleep_test_id = cursor.lastrowid

sleep_questions = [
"How often do you have trouble sleeping at night?",
"How often do you feel tired during the day?",
"How often do academic worries disturb your sleep?",
"How often do you wake up feeling refreshed?",
"How often do you feel physically drained?"
]

for q in sleep_questions:
    cursor.execute("""
    INSERT INTO questions
    (test_id,question_text,option1,option2,option3,option4)
    VALUES (?,?,?,?,?,?)
    """,(
        sleep_test_id,
        q,
        "Never",
        "Sometimes",
        "Often",
        "Always"
    ))

conn.commit()
conn.close()

print("✅ Tests + Questions inserted")