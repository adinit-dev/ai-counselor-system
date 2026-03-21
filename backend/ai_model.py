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

    import random

    insight_parts = []

    # ---------------- RISK INTRO (VARIATION) ----------------
    risk_msgs = {
        "HIGH": [
            "Student is currently in a high-risk state and needs immediate attention.",
            "This student falls under high risk and requires urgent support.",
            "Warning: Student is at high risk and intervention is recommended."
        ],
        "MEDIUM": [
            "Student is at moderate risk and should be monitored closely.",
            "There are signs of moderate risk; guidance is needed.",
            "Student shows medium risk and requires attention."
        ],
        "LOW": [
            "Student is currently stable with low risk.",
            "No major concerns detected; student is in a safe range.",
            "Student appears to be in a low-risk condition."
        ]
    }

    insight_parts.append(random.choice(risk_msgs.get(risk, ["Risk level could not be determined."])))

    # ---------------- ATTENDANCE ----------------
    if attendance < 50:
        insight_parts.append(random.choice([
            f"Attendance is critically low at {attendance:.1f}%, indicating disengagement.",
            f"With attendance at just {attendance:.1f}%, the student is highly inconsistent.",
            f"Low attendance ({attendance:.1f}%) suggests lack of participation."
        ]))
    elif attendance < 75:
        insight_parts.append(random.choice([
            f"Attendance is moderate at {attendance:.1f}%, showing partial consistency.",
            f"Attendance ({attendance:.1f}%) is acceptable but needs improvement.",
            f"Student attends moderately ({attendance:.1f}%), but consistency can improve."
        ]))
    else:
        insight_parts.append(random.choice([
            f"Attendance is strong at {attendance:.1f}%, indicating discipline.",
            f"High attendance ({attendance:.1f}%) reflects good consistency.",
            f"Student maintains solid attendance ({attendance:.1f}%)."
        ]))

    # ---------------- MARKS ----------------
    if marks < 50:
        insight_parts.append(random.choice([
            f"Academic performance is weak at {marks:.1f}%.",
            f"Marks are low ({marks:.1f}%), indicating learning gaps.",
            f"Student is struggling academically with {marks:.1f}%."
        ]))
    elif marks < 75:
        insight_parts.append(random.choice([
            f"Performance is average at {marks:.1f}%.",
            f"Marks ({marks:.1f}%) indicate moderate understanding.",
            f"Student shows average academic performance ({marks:.1f}%)."
        ]))
    else:
        insight_parts.append(random.choice([
            f"Performance is strong at {marks:.1f}%.",
            f"Marks ({marks:.1f}%) reflect good understanding.",
            f"Student is performing well academically ({marks:.1f}%)."
        ]))

    # ---------------- PATTERN ANALYSIS ----------------
    if attendance < 50 and marks < 50:
        insight_parts.append(random.choice([
            "Student is both disengaged and academically struggling.",
            "Low participation and weak performance indicate serious concern.",
        ]))
    elif attendance > 75 and marks < 50:
        insight_parts.append(random.choice([
            "Student attends regularly but struggles with understanding concepts.",
            "Despite good attendance, academic performance is lacking.",
        ]))
    elif attendance < 50 and marks > 70:
        insight_parts.append(random.choice([
            "Student has capability but lacks consistency in attendance.",
            "Performance is good, but attendance issues are limiting potential.",
        ]))
    elif attendance > 75 and marks > 75:
        insight_parts.append(random.choice([
            "Student is consistent and performing very well.",
            "Strong attendance and performance indicate excellent stability.",
        ]))
    else:
        insight_parts.append(random.choice([
            "Student shows mixed performance and needs monitoring.",
            "There is inconsistency in performance that requires attention.",
        ]))

    # ---------------- MENTAL STATE ----------------
    if mental_score is not None:
        if mental_score >= 8:
            insight_parts.append(random.choice([
                "Mental assessment suggests high stress levels.",
                "Student appears to be under significant emotional pressure.",
            ]))
        elif mental_score >= 5:
            insight_parts.append(random.choice([
                "Moderate emotional pressure is observed.",
                "Student shows signs of manageable stress.",
            ]))
        else:
            insight_parts.append(random.choice([
                "Mental condition appears stable.",
                "No major emotional concerns detected.",
            ]))

    # ---------------- FUTURE PREDICTION ----------------
    if risk == "HIGH":
        insight_parts.append(random.choice([
            "Without intervention, performance may decline further.",
            "Immediate support is required to prevent deterioration.",
        ]))
    elif risk == "MEDIUM":
        insight_parts.append(random.choice([
            "Performance may fluctuate if not supported.",
            "Guidance can help stabilize performance.",
        ]))
    else:
        insight_parts.append(random.choice([
            "Student is likely to remain stable if current trends continue.",
            "Consistent effort can further improve performance.",
        ]))

    # ---------------- RECOMMENDATION ----------------
    if risk == "HIGH":
        insight_parts.append(random.choice([
            "Recommended: Immediate counseling and close monitoring.",
            "Action: Reduce pressure and provide structured support.",
        ]))
    elif risk == "MEDIUM":
        insight_parts.append(random.choice([
            "Recommended: Regular mentoring and better study planning.",
            "Action: Provide guidance and emotional support.",
        ]))
    else:
        insight_parts.append(random.choice([
            "Recommended: Maintain current routine and encourage growth.",
            "Action: Continue consistent efforts and build on strengths.",
        ]))

    return " ".join(insight_parts)