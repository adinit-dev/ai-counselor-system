from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import uuid
from ai_model import generate_ai_insight

app = Flask(__name__)
CORS(app,
     supports_credentials=True,
     resources={r"/*": {"origins": "*"}},
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "database", "mental_health.db")
DB_PATH = os.path.abspath(DB_PATH)

@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
    return response

# ---------------- LOGIN ----------------
@app.route('/login', methods=['POST'])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email.endswith("@nitap.ac.in"):
        return jsonify({"status":"invalid_domain"})

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
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row

        rows = conn.execute("SELECT * FROM tests").fetchall()

        tests = []
        for row in rows:
            tests.append({
                "id": row["id"],
                "title": row["title"]   # ✅ IMPORTANT
            })

        conn.close()

        return jsonify(tests)

    except Exception as e:
        print("ERROR IN /tests:", e)   # 👈 will show real error
        return jsonify({"error": str(e)}), 500


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

@app.route("/test/<int:test_id>", methods=["GET"])
def get_test(test_id):

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # ✅ FIXED COLUMN
    cursor.execute("SELECT title FROM tests WHERE id=?", (test_id,))
    test = cursor.fetchone()

    conn.close()

    return {
        "title": test["title"]
    }

# ---------------- CREATE TEST ----------------
@app.route("/create_test", methods=["POST"])
def create_test():
    try:
        data = request.json
        title = data.get("title")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO tests (title) VALUES (?)",
            (title,)
        )

        test_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "test_id": test_id
        })

    except Exception as e:
        print("CREATE TEST ERROR:", e)
        return jsonify({"success": False}), 500


# ---------------- ADD QUESTION ----------------
@app.route("/add_question", methods=["POST"])
def add_question():

    data = request.json

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO questions
        (test_id, question_text, option1, option2, option3, option4)
        VALUES (?,?,?,?,?,?)
    """, (
        data["test_id"],
        data["question_text"],   # ✅ FIXED
        data["option1"],
        data["option2"],
        data["option3"],
        data["option4"]
    ))

    conn.commit()
    conn.close()

    return jsonify({"success": True})

# ---------------- SUBMIT RESPONSE ----------------
@app.route("/submit_response", methods=["POST"])
def submit_response():

    data = request.json

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM responses
        WHERE student_id=? AND test_id=? AND question_id=?
    """, (data["student_id"], data["test_id"], data["question_id"]))

    cursor.execute(
        "INSERT INTO responses (student_id, test_id, question_id, answer) VALUES (?, ?, ?, ?)",
        (data["student_id"], data["test_id"], data["question_id"], data["answer"])
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

    score = sum(score_map.get(ans, 0) for ans in answers)

    if score <= 5:
        return score, "Low"
    elif score <= 10:
        return score, "Medium"
    else:
        return score, "High"


# ---------------- FINISH TEST ----------------
@app.route("/finish_test", methods=["POST"])
def finish_test():

    data = request.json

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT answer
        FROM responses
        WHERE student_id=? AND test_id=?
    """, (data["student_id"], data["test_id"]))

    answers = [row[0] for row in cursor.fetchall()]

    score, risk = calculate_risk(answers)

    cursor.execute("""
        DELETE FROM results
        WHERE student_id=? AND test_id=?
    """, (data["student_id"], data["test_id"]))

    cursor.execute("""
        INSERT INTO results (student_id, test_id, score, risk)
        VALUES (?, ?, ?, ?)
    """, (data["student_id"], data["test_id"], score, risk))

    conn.commit()
    conn.close()

    return jsonify({"status": "success"})


# ---------------- COUNSELOR RESULTS ----------------
@app.route("/counselor/results")
def counselor_results():

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    students = cursor.execute("""
        SELECT id, name, email FROM students
    """).fetchall()

    results = []

    for s in students:

        student_id = s["id"]

        # ---------------- ATTENDANCE ----------------
        cursor.execute("""
            SELECT COUNT(*),
                   SUM(CASE WHEN status='present' THEN 1 ELSE 0 END)
            FROM attendance_log
            WHERE student_id=?
        """, (student_id,))
        
        row = cursor.fetchone()
        total = row[0] if row and row[0] else 0
        present = row[1] if row and row[1] else 0
        attendance = (present / total) * 100 if total > 0 else 0

        # ---------------- MARKS ----------------
        cursor.execute("""
            SELECT AVG(marks*1.0/max_marks)
            FROM exam_results
            WHERE student_id=?
        """, (student_id,))
        
        row = cursor.fetchone()
        marks = (row[0] if row and row[0] else 0) * 100

        # ---------------- MENTAL SCORE ----------------
        cursor.execute("""
            SELECT AVG(score)
            FROM results
            WHERE student_id=?
        """, (student_id,))
        
        row = cursor.fetchone()
        mental_score = row[0] if row and row[0] else 5

        # ---------------- RISK ----------------
        cursor.execute("""
            SELECT risk FROM results
            WHERE student_id=?
            ORDER BY id DESC LIMIT 1
        """, (student_id,))
        
        row = cursor.fetchone()
        risk = row[0] if row else "LOW"

        # ---------------- SCORE (🔥 REAL FIX) ----------------
        score = (
            (attendance * 0.4) +
            (marks * 0.4) +
            ((10 - mental_score) * 10 * 0.2)
        )

        results.append({
            "id": student_id,
            "name": s["name"],
            "email": s["email"],
            "score": round(score, 2),
            "risk": risk
        })

    conn.close()

    return jsonify(results)




# ---------------- COMPLETED TESTS ----------------
@app.route("/student/completed/<student_id>")
def completed_tests(student_id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
SELECT tests.title, results.score, results.risk
FROM results
JOIN tests ON tests.id = results.test_id
WHERE results.student_id = ?
""", (student_id,))

    rows = cursor.fetchall()

    data = []
    for r in rows:
        data.append({"test_name": r[0]})

    conn.close()
    return jsonify({"tests":data})


# ---------------- SIGNUP ----------------
@app.route("/student_signup", methods=["POST"])
def student_signup():

    data = request.json

    if not data["email"].endswith("@nitap.ac.in"):
        return jsonify({"status": "invalid_domain"})

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO students (name,email,password)
        VALUES (?,?,?)
    """,(data["name"],data["email"],data["password"]))

    student_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return jsonify({
        "status":"success",
        "id":student_id,
        "name":data["name"]
    })

@app.route("/student_profile/<int:student_id>")
def student_profile(student_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # ---------------- ATTENDANCE ----------------
        cursor.execute("""
            SELECT COUNT(*),
                   SUM(CASE WHEN status='present' THEN 1 ELSE 0 END)
            FROM attendance_log
            WHERE student_id=?
        """, (student_id,))
        
        row = cursor.fetchone()
        total = row[0] if row and row[0] else 0
        present = row[1] if row and row[1] else 0
        attendance = (present / total) * 100 if total > 0 else 0

        # ---------------- MARKS ----------------
        cursor.execute("""
            SELECT AVG(marks*1.0/max_marks)
            FROM exam_results
            WHERE student_id=?
        """, (student_id,))
        
        row = cursor.fetchone()
        marks = (row[0] if row and row[0] else 0) * 100

        # ---------------- RISK ----------------
        cursor.execute("""
            SELECT risk FROM results
            WHERE student_id=?
            ORDER BY id DESC LIMIT 1
        """, (student_id,))
        
        row = cursor.fetchone()
        risk = row[0] if row else "Unknown"

        conn.close()

        # ---------------- AI INSIGHT ----------------
        try:
            insight = generate_ai_insight(attendance, marks, risk)
            print("AI OUTPUT:", insight)
        except Exception as e:
            print("AI ERROR:", e)
            insight = f"Basic insight: Attendance {attendance:.1f}%, Marks {marks:.1f}%, Risk {risk}"

        return jsonify({
            "attendance": round(attendance, 2),
            "marks": round(marks, 2),
            "risk": risk,
            "ai_insight": insight
        })

    except Exception as e:
        print("AI ERROR:", e)



@app.route("/counselor_login", methods=["POST"])
def counselor_login():

    data = request.json

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM counselors WHERE email=? AND password=?",
        (data["email"], data["password"])
    )

    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({
            "status": "success",
            "id": user[0]
        })

    return jsonify({"status": "fail"})

if __name__ == "__main__":
    app.run(debug=True)