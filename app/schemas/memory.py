from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class UserContextBase(BaseModel):
    key: str
    value: str


class UserContextCreate(UserContextBase):
    override: bool = False


class UserContextUpdate(BaseModel):
    value: str


class UserContextResponse(UserContextBase):
    id: int
    user_id: int
    confidence_score: float
    usage_count: int
    learned_from_conversation_id: Optional[str] = None
    last_used: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserContextSummary(BaseModel):
    writing_style: Optional[str] = None
    industry: Optional[str] = None
    tone_preference: Optional[str] = None
    target_audience: Optional[str] = None
    favorite_templates: List[str] = []
    learned_from: Dict[str, str] = {}


class ConversationSearchRequest(BaseModel):
    query: str
    limit: int = 10


class ConversationSearchResult(BaseModel):
    conversation_id: str
    title: str
    snippet: str
    relevance_score: float
    date: datetime


class ConversationSearchResponse(BaseModel):
    results: List[ConversationSearchResult]
    total: int