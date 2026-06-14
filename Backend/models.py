from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    role = Column(String(20), nullable=False) # "candidate", "recruiter", "interviewer"

    candidate_profile = relationship("CandidateProfile", back_populates="user", uselist=False)
    
    candidate_interviews = relationship("Interview", foreign_keys="Interview.candidate_id", back_populates="candidate")
    recruiter_interviews = relationship("Interview", foreign_keys="Interview.recruiter_id", back_populates="recruiter")
    interviewer_interviews = relationship("Interview", foreign_keys="Interview.interviewer_id", back_populates="interviewer")

class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    skills = Column(Text, nullable=True)
    years_of_experience = Column(Float, default=0.0)
    education_level = Column(String(50), default="Bachelors")

    user = relationship("User", back_populates="candidate_profile")

class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recruiter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    interviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    position = Column(String(100), nullable=False)
    scheduled_time = Column(String(100), nullable=False)
    status = Column(String(20), default="Scheduled")
    
    candidate = relationship("User", foreign_keys=[candidate_id], back_populates="candidate_interviews")
    recruiter = relationship("User", foreign_keys=[recruiter_id], back_populates="recruiter_interviews")
    interviewer = relationship("User", foreign_keys=[interviewer_id], back_populates="interviewer_interviews")
    feedback = relationship("Feedback", uselist=False, back_populates="interview")

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), unique=True, nullable=False)
    technical_score = Column(Integer, nullable=False)
    communication_rating = Column(Integer, nullable=False)
    previous_performance = Column(Integer, nullable=False)
    skills_score = Column(Integer, nullable=False)
    comments = Column(Text, nullable=True)
    
    predicted_outcome = Column(String(50), nullable=True)
    predicted_probability = Column(Float, nullable=True)
    
    ai_feedback_summary = Column(Text, nullable=True)
    ai_strengths = Column(Text, nullable=True)
    ai_improvements = Column(Text, nullable=True)
    ai_report = Column(Text, nullable=True)

    interview = relationship("Interview", back_populates="feedback")
