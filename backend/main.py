from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="AI Academic Advisor API",
    description="Rule-based student progress analysis and study advice API",
    version="1.0.0",
)

# For a public student demo, allow GitHub Pages and local testing.
# For production, replace "*" with your exact GitHub Pages origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StudentData(BaseModel):
    student_name: str = Field(default="Student", min_length=1, max_length=80)
    total_subjects: int = Field(ge=1, le=30)
    completed_subjects: int = Field(ge=0, le=30)
    planned_hours: float = Field(ge=0, le=168)
    actual_hours: float = Field(ge=0, le=168)
    average_mark: float = Field(ge=0, le=100)
    confidence: int = Field(ge=1, le=5)
    exam_days: int = Field(ge=0, le=365)
    pending_topics: List[str] = Field(default_factory=list, max_length=100)

class AdviceRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    student: StudentData

@app.get("/")
def root():
    return {"message": "AI Academic Advisor backend is running", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok", "message": "FastAPI backend is running"}

def clamp(value, low=0, high=100):
    return max(low, min(high, value))

def analyze_student(s: StudentData):
    completion = round(s.completed_subjects / s.total_subjects * 100)
    time_achievement = round(min(100, s.actual_hours / s.planned_hours * 100)) if s.planned_hours > 0 else (100 if s.actual_hours == 0 else 100)
    # Transparent rule-based score, not a trained ML prediction.
    risk = 0
    risk += max(0, 40 - completion) * 0.7
    risk += max(0, 60 - s.average_mark) * 0.6
    risk += max(0, 70 - time_achievement) * 0.25
    risk += (5 - s.confidence) * 5
    risk += max(0, 7 - s.exam_days) * 2.5
    if s.pending_topics:
        risk += min(15, len(s.pending_topics) * 2)
    risk = int(round(clamp(risk)))
    level = "Low" if risk < 30 else "Moderate" if risk < 60 else "High"

    recommendations = []
    if completion < 50:
        recommendations.append("Prioritize unfinished syllabus; divide each subject into small topics.")
    if time_achievement < 80:
        recommendations.append("Set a realistic daily study target and record actual time at the end of the day.")
    if s.average_mark < 60:
        recommendations.append("Use active recall and solve practice questions, then review mistakes.")
    if s.confidence <= 2:
        recommendations.append("Start with one easy topic, study for 25 minutes, and explain it in your own words.")
    if s.exam_days <= 7:
        recommendations.append("An exam is close: revise high-priority topics and practise past questions.")
    if s.pending_topics:
        recommendations.append("Complete the pending topics one at a time; avoid scheduling every topic in one day.")
    if not recommendations:
        recommendations.append("Maintain your current routine and review progress at the end of the week.")

    topics = s.pending_topics[:]
    if not topics:
        topics = ["Review the hardest topic", "Practise questions", "Revise notes"]
    study_plan = []
    for i, topic in enumerate(topics[:7]):
        study_plan.append(f"Session {i+1}: Study '{topic}' for 25 minutes, take a 5-minute break, then answer 3 practice questions.")
    if len(study_plan) < 3:
        study_plan.extend([
            "Next session: revise yesterday's notes for 15 minutes.",
            "Final session: take a short self-test and note topics to revisit."
        ])
    return {
        "student_name": s.student_name,
        "syllabus_completion": completion,
        "study_time_achievement": time_achievement,
        "risk_score": risk,
        "risk_level": level,
        "summary": f"{completion}% of subjects marked complete; study-time target achievement is {time_achievement}%. This is a rule-based estimate, not a validated prediction.",
        "recommendations": recommendations,
        "study_plan": study_plan,
    }

@app.post("/api/analyze")
def analyze(s: StudentData):
    if s.completed_subjects > s.total_subjects:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Completed subjects cannot exceed total subjects.")
    return analyze_student(s)

@app.post("/api/advice")
def advice(req: AdviceRequest):
    q = req.question.lower()
    s = req.student
    result = analyze_student(s)
    if any(word in q for word in ["exam", "test", "tomorrow", "days"]):
        answer = (
            f"Your current rule-based risk level is {result['risk_level']} ({result['risk_score']}/100). "
            f"You have {s.exam_days} day(s) until the exam. Start with the most important pending topic, "
            "study in 25-minute sessions, take short breaks, and solve practice questions. "
            "Do not sacrifice sleep to cover everything."
        )
    elif any(word in q for word in ["time", "schedule", "timetable", "plan", "routine"]):
        answer = "Try this routine: 25 minutes on one pending topic, 5-minute break, 25 minutes of practice, then 10 minutes to review mistakes. Record your actual study time honestly."
    elif any(word in q for word in ["mark", "score", "grade", "improve"]):
        answer = "To improve marks, practise questions before rereading notes, keep an error log, and revisit wrong answers after one day. Aim for consistent short sessions."
    elif any(word in q for word in ["stress", "tired", "overwhelmed", "anxious"]):
        answer = "Reduce the workload into one small next action. Take a short break, drink water, and contact a trusted person or college support if stress feels difficult to manage."
    else:
        answer = f"Based on your current inputs, your risk level is {result['risk_level']} ({result['risk_score']}/100). First, work on: {result['recommendations'][0]} This is rule-based guidance, not a trained AI chatbot."
    return {"answer": answer, "risk_level": result["risk_level"], "risk_score": result["risk_score"]}
