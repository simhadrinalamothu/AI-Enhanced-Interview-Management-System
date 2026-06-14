from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import os

from . import models, schemas, crud, ml_predict, genai_report
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI-Enhanced Interview Management System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "AI-Enhanced Interview Management System API is running successfully!"}

@app.post("/api/auth/register", response_model=schemas.UserWithProfileOut)
def register_user(user_in: schemas.UserCreate, profile_in: Optional[schemas.CandidateProfileBase] = None, db: Session = Depends(get_db)):
    db_user_username = crud.get_user_by_username(db, username=user_in.username)
    if db_user_username:
        raise HTTPException(status_code=400, detail="Username already registered")
        
    db_user_email = crud.get_user_by_email(db, email=user_in.email)
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    # Enforce corporate domain for admin roles
    if user_in.role in ["recruiter", "interviewer"]:
        if not user_in.email.endswith("@company.com"):
            raise HTTPException(status_code=400, detail="Administrative registration requires a corporate @company.com email address")
            
    new_user = crud.create_user(db, user=user_in)
    
    if new_user.role == "candidate":
        profile_data = profile_in.dict() if profile_in else {
            "full_name": new_user.username.capitalize(),
            "skills": "",
            "years_of_experience": 0.0,
            "education_level": "Bachelors"
        }
        profile_create = schemas.CandidateProfileCreate(
            user_id=new_user.id,
            **profile_data
        )
        crud.create_candidate_profile(db, profile=profile_create)
        
    db.refresh(new_user)
    return new_user

@app.post("/api/auth/login")
def login_user(login_in: schemas.UserLogin, db: Session = Depends(get_db)):
    # Look up by username, or by email if not found
    db_user = crud.get_user_by_username(db, username=login_in.username)
    if not db_user:
        db_user = crud.get_user_by_email(db, email=login_in.username)
        
    if not db_user or not crud.verify_password(login_in.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid username or password")
        
    profile = None
    if db_user.role == "candidate":
        profile_obj = crud.get_candidate_profile(db, user_id=db_user.id)
        if profile_obj:
            profile = {
                "id": profile_obj.id,
                "full_name": profile_obj.full_name,
                "skills": profile_obj.skills,
                "years_of_experience": profile_obj.years_of_experience,
                "education_level": profile_obj.education_level
            }
            
    return {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "role": db_user.role,
        "candidate_profile": profile
    }

@app.get("/api/users/candidates", response_model=List[schemas.UserWithProfileOut])
def list_candidates(db: Session = Depends(get_db)):
    return crud.get_users_by_role(db, role="candidate")

@app.get("/api/users/interviewers", response_model=List[schemas.UserOut])
def list_interviewers(db: Session = Depends(get_db)):
    return crud.get_users_by_role(db, role="interviewer")

@app.get("/api/users/recruiters", response_model=List[schemas.UserOut])
def list_recruiters(db: Session = Depends(get_db)):
    return crud.get_users_by_role(db, role="recruiter")

@app.get("/api/interviews", response_model=List[schemas.InterviewOut])
def get_all_interviews(db: Session = Depends(get_db)):
    return crud.get_all_interviews(db)

@app.get("/api/interviews/user/{user_id}", response_model=List[schemas.InterviewOut])
def get_user_interviews(user_id: int, role: str, db: Session = Depends(get_db)):
    return crud.get_interviews_for_user(db, user_id=user_id, role=role)

@app.post("/api/interviews", response_model=schemas.InterviewOut)
def schedule_interview(interview_in: schemas.InterviewCreate, db: Session = Depends(get_db)):
    candidate = crud.get_user(db, interview_in.candidate_id)
    recruiter = crud.get_user(db, interview_in.recruiter_id)
    interviewer = crud.get_user(db, interview_in.interviewer_id)
    
    if not candidate or candidate.role != "candidate":
        raise HTTPException(status_code=404, detail="Candidate not found")
    if not recruiter or recruiter.role != "recruiter":
        raise HTTPException(status_code=404, detail="Recruiter not found")
    if not interviewer or interviewer.role != "interviewer":
        raise HTTPException(status_code=404, detail="Interviewer not found")
        
    return crud.create_interview(db, interview=interview_in)

@app.put("/api/interviews/{interview_id}/status", response_model=schemas.InterviewOut)
def update_status(interview_id: int, status_in: schemas.InterviewUpdate, db: Session = Depends(get_db)):
    db_interview = crud.update_interview_status(db, interview_id=interview_id, status=status_in.status)
    if not db_interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return db_interview

@app.get("/api/interviews/{interview_id}/detail", response_model=schemas.InterviewDetailOut)
def get_interview_detail(interview_id: int, db: Session = Depends(get_db)):
    db_interview = crud.get_interview(db, interview_id)
    if not db_interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return db_interview

@app.post("/api/feedback", response_model=schemas.FeedbackOut)
def submit_interview_feedback(feedback_in: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    db_feedback = crud.get_feedback_by_interview_id(db, interview_id=feedback_in.interview_id)
    if db_feedback:
        raise HTTPException(status_code=400, detail="Feedback already submitted for this interview")
        
    db_interview = crud.get_interview(db, feedback_in.interview_id)
    if not db_interview:
        raise HTTPException(status_code=404, detail="Interview not found")
        
    candidate_profile = crud.get_candidate_profile(db, user_id=db_interview.candidate_id)
    if not candidate_profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
        
    predicted_outcome, predicted_prob = ml_predict.predict_candidate_selection(
        experience=candidate_profile.years_of_experience,
        skills_score=feedback_in.skills_score,
        technical_score=feedback_in.technical_score,
        communication=feedback_in.communication_rating,
        previous=feedback_in.previous_performance,
        education=candidate_profile.education_level
    )
    
    ai_data = genai_report.generate_interview_evaluation_report(
        candidate_name=candidate_profile.full_name,
        position=db_interview.position,
        skills=candidate_profile.skills or "",
        experience=candidate_profile.years_of_experience,
        tech_score=feedback_in.technical_score,
        comm_rating=feedback_in.communication_rating,
        prev_performance=feedback_in.previous_performance,
        comments=feedback_in.comments or "",
        outcome=predicted_outcome
    )
    
    feedback_record = crud.create_feedback(
        db=db,
        feedback=feedback_in,
        pred_outcome=predicted_outcome,
        pred_prob=predicted_prob,
        ai_data=ai_data
    )
    
    return feedback_record

@app.get("/api/dashboard/stats", response_model=schemas.DashboardStats)
def get_stats(db: Session = Depends(get_db)):
    return crud.get_dashboard_stats(db)

# Mount frontend static files
from fastapi.staticfiles import StaticFiles
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Frontend"))
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

