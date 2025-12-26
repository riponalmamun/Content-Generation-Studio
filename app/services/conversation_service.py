from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.conversation import Conversation, Message
from app.models.memory import ConversationSummary
from app.services.openai_service import openai_service
from app.services.memory_service import MemoryService
from app.services.embedding_service import EmbeddingService
from app.utils.helpers import generate_conversation_title, calculate_credits, calculate_cost
from datetime import datetime
import uuid


class ConversationService:
    def __init__(self, db: Session):
        self.db = db
        self.memory_service = MemoryService(db)
        self.embedding_service = EmbeddingService(db)
    
    def create_conversation(
        self,
        user_id: int,
        title: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Conversation:
        """Create new conversation"""
        conversation = Conversation(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title or "New Conversation",
            session_id=session_id or str(uuid.uuid4())
        )
        
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation
    
    def get_conversation(
        self,
        conversation_id: str,
        user_id: int
    ) -> Optional[Conversation]:
        """Get conversation by ID"""
        return self.db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()
    
    def list_conversations(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> List[Conversation]:
        """List user's conversations"""
        return self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(desc(Conversation.updated_at)).limit(limit).offset(offset).all()
    
    def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        tokens_used: int = 0,
        model_used: Optional[str] = None
    ) -> Message:
        """Save message to conversation"""
        message = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            role=role,
            content=content,
            tokens_used=tokens_used,
            model_used=model_used
        )
        
        self.db.add(message)
        
        # Update conversation timestamp
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        if conversation:
            conversation.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def get_conversation_messages(
        self,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[Message]:
        """Get messages from conversation"""
        query = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_recent_messages(
        self,
        conversation_id: str,
        limit: int = 10
    ) -> List[Dict[str, str]]:
        """Get recent messages formatted for OpenAI"""
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(desc(Message.created_at)).limit(limit).all()
        
        # Reverse to chronological order
        messages.reverse()
        
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
    
    async def chat_with_memory(
        self,
        user_id: int,
        message: str,
        conversation_id: Optional[str] = None,
        content_type: str = "default",
        use_memory: bool = True,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Main chat function with memory"""
        
        # Get or create conversation
        if not conversation_id:
            conversation = self.create_conversation(user_id)
            conversation_id = conversation.id
            
            # Generate title from first message
            title = generate_conversation_title(message)
            conversation.title = title
            self.db.commit()
        else:
            conversation = self.get_conversation(conversation_id, user_id)
            if not conversation:
                raise ValueError("Conversation not found")
        
        # Get user context
        user_context = {}
        if use_memory:
            user_context = self.memory_service.get_user_context(user_id)
        
        # Get conversation history
        conversation_history = self.get_recent_messages(conversation_id, limit=10)
        
        # Generate response
        response_data = await openai_service.generate_with_context(
            user_message=message,
            content_type=content_type,
            user_context=user_context,
            conversation_history=conversation_history,
            model=model
        )
        
        assistant_message = response_data["content"]
        tokens_used = response_data["tokens_used"]
        model_used = response_data["model_used"]
        
        # Save messages
        self.save_message(
            conversation_id=conversation_id,
            role="user",
            content=message,
            tokens_used=0
        )
        
        assistant_msg = self.save_message(
            conversation_id=conversation_id,
            role="assistant",
            content=assistant_message,
            tokens_used=tokens_used,
            model_used=model_used
        )
        
        # Generate embeddings in background (non-blocking)
        try:
            await self.embedding_service.generate_and_store_embedding(
                assistant_msg.id, assistant_message
            )
        except Exception as e:
            print(f"Embedding generation failed: {str(e)}")
        
        # Extract and update context
        if use_memory:
            try:
                learned_context = await self.memory_service.extract_and_save_context(
                    user_id=user_id,
                    conversation_id=conversation_id,
                    user_message=message,
                    assistant_message=assistant_message
                )
            except Exception as e:
                print(f"Context extraction failed: {str(e)}")
                learned_context = {}
        else:
            learned_context = {}
        
        return {
            "conversation_id": conversation_id,
            "response": assistant_message,
            "tokens_used": tokens_used,
            "model_used": model_used,
            "credits_used": calculate_credits(model_used, tokens_used),
            "context_applied": user_context,
            "learned_context": learned_context
        }
    
    async def generate_conversation_summary(
        self,
        conversation_id: str
    ) -> Optional[ConversationSummary]:
        """Generate and save conversation summary"""
        messages = self.get_recent_messages(conversation_id)
        
        if not messages:
            return None
        
        # Generate summary
        summary_text = await openai_service.summarize_conversation(messages)
        
        # Check if summary exists
        existing = self.db.query(ConversationSummary).filter(
            ConversationSummary.conversation_id == conversation_id
        ).first()
        
        if existing:
            existing.summary = summary_text
            existing.updated_at = datetime.utcnow()
        else:
            existing = ConversationSummary(
                id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                summary=summary_text,
                key_points=[]
            )
            self.db.add(existing)
        
        self.db.commit()
        self.db.refresh(existing)
        return existing
    
    def delete_conversation(self, conversation_id: str, user_id: int) -> bool:
        """Delete conversation"""
        conversation = self.get_conversation(conversation_id, user_id)
        if conversation:
            self.db.delete(conversation)
            self.db.commit()
            return True
        return False