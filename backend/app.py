from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import uuid

app = Flask(__name__)

CORS(app)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "mental_health.db")

# ---------------- LOGIN ----------------
@app.route('/login', methods=['POST'])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id,name FROM students WHERE email=? AND password=?",
        (email,password)
    )

    user = cursor.fetchone()

    conn.close()

    if user:
        return jsonify({
            "status":"success",
            "id":user[0],
            "name":user[1]
        })
    else:
        return jsonify({"status":"error"})
    



# ---------------- GET TESTS ----------------
@app.route("/tests")
def get_tests():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id,test_name FROM tests")

    rows = cursor.fetchall()

    tests = []

    for row in rows:
        tests.append({
            "id": row[0],
            "test_name": row[1]
        })

    conn.close()

    return jsonify({"tests": tests})




# ---------------- GET QUESTIONS ----------------

@app.route("/questions/<test_id>")
def get_questions(test_id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
    "SELECT id,question_text,option1,option2,option3,option4 FROM questions WHERE test_id=?",
    (test_id,)
)

    rows = cursor.fetchall()

    questions=[]

    for r in rows:
        questions.append({
            "id": r[0],
            "question": r[1],
            "option1": r[2],
            "option2": r[3],
            "option3": r[4],
            "option4": r[5]
    })

    conn.close()

    return jsonify({"questions":questions})


# ---------------- GET TEST NAME ----------------
@app.route("/test/<int:test_id>", methods=["GET"])
def get_test(test_id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT test_name FROM tests WHERE id=?", (test_id,))
    test = cursor.fetchone()

    conn.close()

    return {"name": test[0]}


# ---------------- CREATE TEST ----------------
@app.route("/create_test", methods=["POST"])
def create_test():

    data = request.json
    name = data["name"]

    test_id = str(uuid.uuid4())

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tests(id,test_name) VALUES (?,?)",
        (test_id, name)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "test_id": test_id
    })


# ---------------- ADD QUESTION ----------------
@app.route("/add_question", methods=["POST"])
def add_question():

    data = request.json

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO questions
        (test_id, question_text, option1, option2, option3, option4)
        VALUES (?,?,?,?,?,?)
        """,
        (
            data["test_id"],
            data["question"],
            data["option1"],
            data["option2"],
            data["option3"],
            data["option4"]
        )
    )

    conn.commit()
    conn.close()

    return jsonify({"success": True})


# ---------------- SUBMIT RESPONSE ----------------
@app.route("/submit_response", methods=["POST"])
def submit_response():

    data = request.json
    student_id = data["student_id"]
    test_id = data["test_id"]
    question_id = data["question_id"]
    answer = data["answer"]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # delete old response for this student + test + question
    cursor.execute("""
        DELETE FROM responses
        WHERE student_id=? AND test_id=? AND question_id=?
    """, (student_id, test_id, question_id))

    # insert new response
    cursor.execute(
        "INSERT INTO responses (student_id, test_id, question_id, answer) VALUES (?, ?, ?, ?)",
        (student_id, test_id, question_id, answer)
    )

    conn.commit()
    conn.close()

    return {"status": "saved"}


# ---------------- RISK CALCULATION ----------------
def calculate_risk(answers):

    score_map = {
        "Never": 0,
        "Sometimes": 1,
        "Often": 2,
        "Always": 3
    }

    score = 0

    for ans in answers:
        score += score_map.get(ans, 0)

    if score <= 5:
        return score, "Low"
    elif score <= 10:
        return score, "Medium"
    else:
        return score, "High"
    




# ---------------- COUNSELOR RESULTS ----------------
@app.route("/counselor/results")
def counselor_results():

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    students = conn.execute("""
        SELECT id, name, email
        FROM students
    """).fetchall()

    results = []

    for s in students:

        answers = conn.execute("""
            SELECT answer
            FROM responses
            WHERE student_id = ?
        """, (s["id"],)).fetchall()

        answer_list = [a["answer"] for a in answers]

        if len(answer_list) == 0:
            continue

        score, risk = calculate_risk(answer_list)

        results.append({
            "name": s["name"],
            "email": s["email"],
            "score": score,
            "risk": risk
        })

    conn.close()

    return jsonify(results)

@app.route("/student/completed/<student_id>")
def completed_tests(student_id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT tests.test_name
    FROM results
    JOIN tests ON results.test_id = tests.id
    WHERE results.student_id = ?
    """,(student_id,))

    rows = cursor.fetchall()

    data = []

    for r in rows:
        data.append({
            "test_name": r[0]
        })

    conn.close()

    return jsonify({"tests":data})

# ---------------- FINALIZE TEST ----------------
@app.route("/finish_test", methods=["POST"])
def finish_test():

    data = request.json
    student_id = data["student_id"]
    test_id = data["test_id"]

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    answers = cursor.execute("""
        SELECT answer FROM responses
        WHERE student_id=? AND test_id=?
    """,(student_id,test_id)).fetchall()

    answer_list = [a["answer"] for a in answers]

    score, risk = calculate_risk(answer_list)

    cursor.execute("""
        INSERT INTO results(student_id,test_id,score,risk)
        VALUES(?,?,?,?)
    """,(student_id,test_id,score,risk))

    conn.commit()
    conn.close()

    return jsonify({
        "status":"saved",
        "score":score,
        "risk":risk
    })

@app.route("/counselor_login", methods=["POST"])
def counselor_login():

    data = request.json
    email = data["email"]
    password = data["password"]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id,name FROM counselors WHERE email=? AND password=?",
        (email,password)
    )

    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({
            "status":"success",
            "id":user[0],
            "name":user[1]
        })

    return jsonify({"status":"fail"})


print("Using DB:", os.path.abspath("database/mental_health.db"))


import uuid

import uuid




if __name__ == "__main__":
    app.run(debug=True)
