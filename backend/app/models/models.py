import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sessions = relationship("Session", back_populates="user")
    exam_attempts = relationship("ExamAttempt", back_populates="user")
    game_sessions = relationship("GameSession", back_populates="user")

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    session_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("sessions.id"))
    content = Column(Text)
    role = Column(String)  # user, assistant
    created_at = Column(DateTime, default=datetime.utcnow)
    session = relationship("Session", back_populates="messages")

class Exam(Base):
    __tablename__ = "exams"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String)
    description = Column(Text, nullable=True)
    topic = Column(String)
    difficulty = Column(String)  # easy, medium, hard
    created_at = Column(DateTime, default=datetime.utcnow)
    questions = relationship("Question", back_populates="exam")
    attempts = relationship("ExamAttempt", back_populates="exam")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    exam_id = Column(String, ForeignKey("exams.id"))
    question_text = Column(Text)
    question_type = Column(String)  # multiple_choice, open_ended
    options = Column(JSON, nullable=True)  # For multiple choice
    correct_answer = Column(String)  # For multiple choice: index, for open_ended: expected answer
    explanation = Column(Text, nullable=True)
    points = Column(Integer, default=1)
    exam = relationship("Exam", back_populates="questions")

class ExamAttempt(Base):
    __tablename__ = "exam_attempts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    exam_id = Column(String, ForeignKey("exams.id"))
    answers = Column(JSON)  # User's answers
    score = Column(Float)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    user = relationship("User", back_populates="exam_attempts")
    exam = relationship("Exam", back_populates="attempts")

class GameSession(Base):
    __tablename__ = "game_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    game_type = Column(String)  # cache_simulator, binary_converter, etc.
    score = Column(Integer, nullable=True)
    game_data = Column(JSON)  # Game-specific data
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    user = relationship("User", back_populates="game_sessions")