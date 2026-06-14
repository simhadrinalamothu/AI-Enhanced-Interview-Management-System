import hashlib
from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed_password: str) -> bool:
    return hash_password(password) == hashed_password

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users_by_role(db: Session, role: str):
    return db.query(models.User).filter(models.User.role == role).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_pw = hash_password(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_pw,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_candidate_profile(db: Session, user_id: int):
    return db.query(models.CandidateProfile).filter(models.CandidateProfile.user_id == user_id).first()

def create_candidate_profile(db: Session, profile: schemas.CandidateProfileCreate):
    db_profile = models.CandidateProfile(
        user_id=profile.user_id,
        full_name=profile.full_name,
        skills=profile.skills,
        years_of_experience=profile.years_of_experience,
        education_level=profile.education_level
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

def get_interview(db: Session, interview_id: int):
    return db.query(models.Interview).filter(models.Interview.id == interview_id).first()

def get_interviews_for_user(db: Session, user_id: int, role: str):
    if role == "candidate":
        return db.query(models.Interview).filter(models.Interview.candidate_id == user_id).all()
    elif role == "recruiter":
        return db.query(models.Interview).filter(models.Interview.recruiter_id == user_id).all()
    elif role == "interviewer":
        return db.query(models.Interview).filter(models.Interview.interviewer_id == user_id).all()
    return []

def get_all_interviews(db: Session):
    return db.query(models.Interview).all()

def create_interview(db: Session, interview: schemas.InterviewCreate):
    db_interview = models.Interview(
        candidate_id=interview.candidate_id,
        recruiter_id=interview.recruiter_id,
        interviewer_id=interview.interviewer_id,
        position=interview.position,
        scheduled_time=interview.scheduled_time,
        status="Scheduled"
    )
    db.add(db_interview)
    db.commit()
    db.refresh(db_interview)
    return db_interview

def update_interview_status(db: Session, interview_id: int, status: str):
    db_interview = get_interview(db, interview_id)
    if db_interview:
        db_interview.status = status
        db.commit()
        db.refresh(db_interview)
    return db_interview

def get_feedback_by_interview_id(db: Session, interview_id: int):
    return db.query(models.Feedback).filter(models.Feedback.interview_id == interview_id).first()

def create_feedback(db: Session, feedback: schemas.FeedbackCreate, 
                    pred_outcome: str, pred_prob: float, ai_data: dict):
    db_feedback = models.Feedback(
        interview_id=feedback.interview_id,
        technical_score=feedback.technical_score,
        communication_rating=feedback.communication_rating,
        previous_performance=feedback.previous_performance,
        skills_score=feedback.skills_score,
        comments=feedback.comments,
        predicted_outcome=pred_outcome,
        predicted_probability=pred_prob,
        ai_feedback_summary=ai_data.get("summary", ""),
        ai_strengths=ai_data.get("strengths", ""),
        ai_improvements=ai_data.get("improvements", ""),
        ai_report=ai_data.get("report", "")
    )
    db.add(db_feedback)
    
    db_interview = get_interview(db, feedback.interview_id)
    if db_interview:
        db_interview.status = "Completed"
        
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

def get_dashboard_stats(db: Session):
    total_candidates = db.query(models.User).filter(models.User.role == "candidate").count()
    total_interviews = db.query(models.Interview).count()
    pending_interviews = db.query(models.Interview).filter(models.Interview.status == "Scheduled").count()
    completed_interviews = db.query(models.Interview).filter(models.Interview.status == "Completed").count()
    
    outcome_counts = db.query(
        models.Feedback.predicted_outcome, func.count(models.Feedback.id)
    ).group_by(models.Feedback.predicted_outcome).all()
    
    outcomes = {
        "Highly Likely to Select": 0,
        "Moderately Likely to Select": 0,
        "Low Selection Probability": 0
    }
    for label, count in outcome_counts:
        if label in outcomes:
            outcomes[label] = count
            
    return {
        "total_candidates": total_candidates,
        "total_interviews": total_interviews,
        "pending_interviews": pending_interviews,
        "completed_interviews": completed_interviews,
        "outcome_distribution": outcomes
    }
