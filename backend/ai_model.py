import sqlite3
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import os

# ---------------- SAFE DB PATH ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "database", "mental_health.db")
DB_PATH = os.path.abspath(DB_PATH)


# ---------------- TRAIN MODEL ----------------
def train_model():

    conn = sqlite3.connect(DB_PATH)

    attendance = pd.read_sql_query("""
    SELECT student_id,
    COUNT(*) as total,
    SUM(CASE WHEN status='present' THEN 1 ELSE 0 END) as present
    FROM attendance
    GROUP BY student_id
    """, conn)

    attendance["attendance_rate"] = attendance["present"] / attendance["total"]

    marks = pd.read_sql_query("""
    SELECT student_id,
    AVG(marks*1.0/max_marks) as marks_ratio
    FROM marks
    GROUP BY student_id
    """, conn)

    mental = pd.read_sql_query("""
    SELECT student_id,
    AVG(score) as mental_score
    FROM results
    GROUP BY student_id
    """, conn)

    conn.close()

    data = attendance.merge(marks, on="student_id", how="left")
    data = data.merge(mental, on="student_id", how="left")

    data["mental_score"] = data["mental_score"].fillna(5)

    def risk_label(row):
        if row["attendance_rate"] < 0.65 and row["marks_ratio"] < 0.5:
            return "HIGH"
        if row["mental_score"] > 8:
            return "HIGH"
        if row["attendance_rate"] < 0.75:
            return "MEDIUM"
        return "LOW"

    data["risk"] = data.apply(risk_label, axis=1)

    X = data[["attendance_rate", "marks_ratio", "mental_score"]]
    y = data["risk"]

    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)

    return model


# ---------------- GLOBAL MODEL ----------------
model = None

def get_model():
    global model
    if model is None:
        model = train_model()
    return model


# ---------------- PREDICT STUDENT ----------------
def predict_student(student_id):

    conn = sqlite3.connect(DB_PATH)

    # ---------------- CURRENT DATA ----------------
    att = pd.read_sql_query(f"""
    SELECT COUNT(*) as total,
    SUM(CASE WHEN status='present' THEN 1 ELSE 0 END) as present
    FROM attendance
    WHERE student_id = {student_id}
    """, conn)

    marks = pd.read_sql_query(f"""
    SELECT AVG(marks*1.0/max_marks) as marks_ratio
    FROM marks
    WHERE student_id = {student_id}
    """, conn)

    mental = pd.read_sql_query(f"""
    SELECT AVG(score) as mental_score
    FROM results
    WHERE student_id = {student_id}
    """, conn)

    # ---------------- TREND DATA ----------------
    marks_history = pd.read_sql_query(f"""
    SELECT marks*1.0/max_marks as marks_ratio
    FROM marks
    WHERE student_id = {student_id}
    ORDER BY id DESC LIMIT 3
    """, conn)

    attendance_history = pd.read_sql_query(f"""
    SELECT CASE WHEN status='present' THEN 1 ELSE 0 END as present
    FROM attendance
    WHERE student_id = {student_id}
    ORDER BY id DESC LIMIT 5
    """, conn)

    conn.close()

    # ---------------- CALCULATIONS ----------------
    total = att["total"][0] if att["total"][0] else 0
    present = att["present"][0] if att["present"][0] else 0

    attendance_rate = present / total if total > 0 else 0
    marks_ratio = marks["marks_ratio"][0] if marks["marks_ratio"][0] else 0
    mental_score = mental["mental_score"][0] if mental["mental_score"][0] else 5

    # ---------------- TREND DETECTION ----------------
    marks_trend = "stable"

    if len(marks_history) >= 2:
        if marks_history["marks_ratio"].iloc[0] < marks_history["marks_ratio"].iloc[-1] - 0.2:
            marks_trend = "declining"
        elif marks_history["marks_ratio"].iloc[0] > marks_history["marks_ratio"].iloc[-1] + 0.2:
            marks_trend = "improving"

    attendance_trend = "stable"

    if len(attendance_history) >= 3:
        avg_recent = attendance_history["present"].mean()
        if avg_recent < 0.5:
            attendance_trend = "low"

    # ---------------- ML PREDICTION ----------------
    sample = pd.DataFrame(
        [[attendance_rate, marks_ratio, mental_score]],
        columns=["attendance_rate", "marks_ratio", "mental_score"]
    )

    model = get_model()
    prediction = model.predict(sample)[0]

    # ---------------- TREND ADJUSTMENT ----------------
    if marks_trend == "declining" or attendance_trend == "low":
        if prediction == "LOW":
            prediction = "MEDIUM"
        elif prediction == "MEDIUM":
            prediction = "HIGH"

    return prediction, attendance_rate, marks_ratio, mental_score, marks_trend


# ---------------- AI INSIGHT ----------------
def generate_ai_insight(attendance, marks, risk, mental_score=None):

    insight = ""

    # ---------------- CURRENT STATE ----------------
    insight += f"Student shows {risk.lower()} risk. "

    if attendance < 50:
        insight += "Attendance is significantly low, indicating disengagement. "
    elif attendance < 75:
        insight += "Attendance is moderate, showing partial consistency. "
    else:
        insight += "Attendance is strong, indicating discipline. "

    if marks < 50:
        insight += "Academic performance is weak. "
    elif marks < 75:
        insight += "Performance is average. "
    else:
        insight += "Performance is good. "

    # ---------------- PATTERN ANALYSIS ----------------
    insight += "Pattern analysis suggests: "

    if attendance > 75 and marks < 50:
        insight += "student attends classes but struggles to understand concepts. "

    elif attendance < 50 and marks > 70:
        insight += "student has capability but lacks consistency. "

    elif attendance < 50 and marks < 50:
        insight += "student is both disengaged and academically struggling. "

    elif attendance > 75 and marks > 75:
        insight += "student is consistent and performing well. "

    else:
        insight += "mixed performance with scope for improvement. "

    # ---------------- MENTAL BEHAVIOR ----------------
    if mental_score is not None:

        insight += "Mental assessment indicates: "

        if mental_score >= 8:
            insight += "high stress or anxiety levels. "
        elif mental_score >= 5:
            insight += "moderate emotional pressure. "
        else:
            insight += "stable mental condition. "

    # ---------------- FUTURE PREDICTION ----------------
    insight += "If this pattern continues, "

    if risk == "HIGH":
        insight += "the student may face burnout or academic decline. "
    elif risk == "MEDIUM":
        insight += "performance may fluctuate and risk may increase. "
    else:
        insight += "student is likely to remain stable. "

    # ---------------- ACTIONABLE ADVICE ----------------
    insight += "Recommended action: "

    if risk == "HIGH":
        insight += "immediate counseling, reduced academic pressure, and close monitoring."
    elif risk == "MEDIUM":
        insight += "regular mentoring, better study planning, and emotional support."
    else:
        insight += "maintain current routine and encourage growth."

    return insight