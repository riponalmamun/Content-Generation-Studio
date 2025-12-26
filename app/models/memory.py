from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class UserContext(Base):
    """User's long-term memory/context storage"""
    __tablename__ = "user_contexts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    key = Column(String, nullable=False, index=True)  # e.g., 'writing_style'
    value = Column(Text, nullable=False)
    
    learned_from_conversation_id = Column(String, ForeignKey("conversations.id"), nullable=True)
    confidence_score = Column(Float, default=0.5)  # 0-1
    
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="user_contexts")


# ❌ ConversationSummary removed from here
# ✅ It's already defined in models/conversation.py
# Don't duplicate model definitions!