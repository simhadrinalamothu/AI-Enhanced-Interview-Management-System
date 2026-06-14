from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import datetime

class UserBase(BaseModel):
    username: str
    email: str
    role: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True

class CandidateProfileBase(BaseModel):
    full_name: str
    skills: Optional[str] = None
    years_of_experience: float = 0.0
    education_level: str = "Bachelors"

class CandidateProfileCreate(CandidateProfileBase):
    user_id: int

class CandidateProfileOut(CandidateProfileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class UserWithProfileOut(UserOut):
    candidate_profile: Optional[CandidateProfileOut] = None

    class Config:
        from_attributes = True

class InterviewCreate(BaseModel):
    candidate_id: int
    recruiter_id: int
    interviewer_id: int
    position: str
    scheduled_time: str

class InterviewUpdate(BaseModel):
    status: str

class InterviewOut(BaseModel):
    id: int
    candidate_id: int
    recruiter_id: int
    interviewer_id: int
    position: str
    scheduled_time: str
    status: str
    
    candidate: UserOut
    recruiter: UserOut
    interviewer: UserOut

    class Config:
        from_attributes = True

class FeedbackCreate(BaseModel):
    interview_id: int
    technical_score: int = Field(..., ge=0, le=100)
    communication_rating: int = Field(..., ge=1, le=5)
    previous_performance: int = Field(..., ge=1, le=5)
    skills_score: int = Field(..., ge=0, le=100)
    comments: Optional[str] = ""

class FeedbackOut(BaseModel):
    id: int
    interview_id: int
    technical_score: int
    communication_rating: int
    previous_performance: int
    skills_score: int
    comments: Optional[str]
    predicted_outcome: Optional[str]
    predicted_probability: Optional[float]
    ai_feedback_summary: Optional[str]
    ai_strengths: Optional[str]
    ai_improvements: Optional[str]
    ai_report: Optional[str]

    class Config:
        from_attributes = True

class InterviewDetailOut(InterviewOut):
    feedback: Optional[FeedbackOut] = None

    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_candidates: int
    total_interviews: int
    pending_interviews: int
    completed_interviews: int
    outcome_distribution: Dict[str, int]
