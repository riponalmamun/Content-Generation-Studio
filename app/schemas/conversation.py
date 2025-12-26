from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    id: str
    conversation_id: str
    role: str
    tokens_used: int
    model_used: Optional[str] = None
    created_at: datetime
    metadata: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True


class ConversationBase(BaseModel):
    title: Optional[str] = None


class ConversationCreate(ConversationBase):
    initial_message: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ConversationResponse(ConversationBase):
    id: str
    user_id: int
    session_id: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    message_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


class ConversationWithMessages(ConversationResponse):
    messages: List[MessageResponse] = []


class ConversationSummaryResponse(BaseModel):
    id: str
    conversation_id: str
    summary: str
    key_points: List[str] = []
    created_at: datetime
    
    class Config:
        from_attributes = True