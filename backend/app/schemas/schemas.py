from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime

# Message Schemas
class MessageBase(BaseModel):
    content: str
    role: str

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: str
    session_id: str
    created_at: datetime
    
    class Config:
        orm_mode = True

# Chat Schemas
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    mode: str = "chat"  # chat, exam, game

class ImageInfo(BaseModel):
    url: str
    alt_text: str
    source: Optional[str] = None

class ChatResponse(BaseModel):
    text: str
    images: Optional[List[ImageInfo]] = None
    special_content: Optional[Dict[str, Any]] = None

# Exam Schemas
class ExamCreate(BaseModel):
    title: str
    description: Optional[str] = None
    topic: str
    difficulty: str = "medium"

class QuestionCreate(BaseModel):
    question_text: str
    question_type: str
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: Optional[str] = None
    points: int = 1

class QuestionResponse(BaseModel):
    id: str
    question_text: str
    question_type: str
    options: Optional[List[str]] = None
    points: int
    
    class Config:
        orm_mode = True

class ExamResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    topic: str
    difficulty: str
    questions: List[QuestionResponse]
    
    class Config:
        orm_mode = True

class SubmitExamRequest(BaseModel):
    exam_id: str
    answers: Dict[str, Union[str, int]]  # question_id -> answer

class ExamResult(BaseModel):
    exam_id: str
    score: float
    total_points: int
    percentage: float
    question_results: List[Dict[str, Any]]
    feedback: str

# Game Schemas
class GameRequest(BaseModel):
    game_type: str
    config: Optional[Dict[str, Any]] = None

class GameAction(BaseModel):
    action: str
    data: Optional[Dict[str, Any]] = None

class GameState(BaseModel):
    game_id: str
    game_type: str
    state: Dict[str, Any]
    message: Optional[str] = None
    completed: bool = False
    score: Optional[int] = None