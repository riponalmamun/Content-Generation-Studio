from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.models.memory import UserContext
from app.services.openai_service import openai_service
from datetime import datetime


class MemoryService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_context(self, user_id: int) -> Dict[str, Any]:
        """Get all user context as dictionary"""
        contexts = self.db.query(UserContext).filter(
            UserContext.user_id == user_id
        ).order_by(desc(UserContext.confidence_score)).all()
        
        result = {}
        for ctx in contexts:
            result[ctx.key] = ctx.value
        
        return result
    
    def get_context_by_key(
        self,
        user_id: int,
        key: str
    ) -> Optional[UserContext]:
        """Get specific context by key"""
        return self.db.query(UserContext).filter(
            UserContext.user_id == user_id,
            UserContext.key == key
        ).first()
    
    def update_or_create_context(
        self,
        user_id: int,
        key: str,
        value: str,
        conversation_id: Optional[str] = None,
        confidence_score: float = 0.8
    ) -> UserContext:
        """Update existing context or create new one"""
        existing = self.get_context_by_key(user_id, key)
        
        if existing:
            existing.value = value
            existing.confidence_score = confidence_score
            existing.learned_from_conversation_id = conversation_id
            existing.updated_at = datetime.utcnow()
        else:
            existing = UserContext(
                user_id=user_id,
                key=key,
                value=value,
                learned_from_conversation_id=conversation_id,
                confidence_score=confidence_score
            )
            self.db.add(existing)
        
        self.db.commit()
        self.db.refresh(existing)
        return existing
    
    def increment_context_usage(self, context_id: int):
        """Increment usage count for context"""
        context = self.db.query(UserContext).filter(
            UserContext.id == context_id
        ).first()
        
        if context:
            context.usage_count += 1
            context.last_used = datetime.utcnow()
            self.db.commit()
    
    async def extract_and_save_context(
        self,
        user_id: int,
        conversation_id: str,
        user_message: str,
        assistant_message: str
    ) -> Dict[str, Any]:
        """Extract context from conversation and save"""
        
        # Use OpenAI to extract context
        extracted = await openai_service.extract_context(
            user_message, assistant_message
        )
        
        saved_contexts = {}
        
        for key, value in extracted.items():
            if value and isinstance(value, str):
                context = self.update_or_create_context(
                    user_id=user_id,
                    key=key,
                    value=value,
                    conversation_id=conversation_id,
                    confidence_score=0.7
                )
                saved_contexts[key] = value
        
        return saved_contexts
    
    def delete_context(self, user_id: int, key: str) -> bool:
        """Delete specific context"""
        context = self.get_context_by_key(user_id, key)
        if context:
            self.db.delete(context)
            self.db.commit()
            return True
        return False
    
    def get_context_summary(self, user_id: int) -> Dict[str, Any]:
        """Get formatted summary of user context"""
        contexts = self.db.query(UserContext).filter(
            UserContext.user_id == user_id
        ).all()
        
        summary = {
            "writing_style": None,
            "industry": None,
            "tone_preference": None,
            "target_audience": None,
            "favorite_templates": [],
            "learned_from": {}
        }
        
        for ctx in contexts:
            if ctx.key in summary:
                summary[ctx.key] = ctx.value
                
                # Add learned from info
                learned_key = f"{ctx.key}_learned_from"
                summary["learned_from"][ctx.key] = (
                    f"{ctx.usage_count} conversations"
                )
        
        return summary