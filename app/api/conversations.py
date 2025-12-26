from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationWithMessages,
    ConversationSummaryResponse
)
from app.services.conversation_service import ConversationService


router = APIRouter()


@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new conversation"""
    service = ConversationService(db)
    
    # Create conversation
    conversation = service.create_conversation(
        user_id=current_user.id,
        title=data.title or "New Conversation"
    )
    
    # If initial message provided, process it
    if data.initial_message:
        result = await service.chat_with_memory(
            user_id=current_user.id,
            message=data.initial_message,
            conversation_id=conversation.id,
            use_memory=True
        )
        
        return {
            **conversation.__dict__,
            "initial_response": result["response"]
        }
    
    return conversation


@router.get("/", response_model=List[ConversationResponse])
def list_conversations(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's conversations"""
    service = ConversationService(db)
    conversations = service.list_conversations(
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )
    
    # Add message count
    result = []
    for conv in conversations:
        conv_dict = conv.__dict__
        conv_dict["message_count"] = len(conv.messages)
        result.append(conv_dict)
    
    return result


@router.get("/{conversation_id}", response_model=ConversationWithMessages)
def get_conversation(
    conversation_id: str,
    include_messages: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversation by ID"""
    service = ConversationService(db)
    
    conversation = service.get_conversation(conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    result = {
        **conversation.__dict__,
        "message_count": len(conversation.messages)
    }
    
    if include_messages:
        result["messages"] = conversation.messages
    else:
        result["messages"] = []
    
    return result


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete conversation"""
    service = ConversationService(db)
    
    success = service.delete_conversation(conversation_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return None


@router.get("/{conversation_id}/summary", response_model=ConversationSummaryResponse)
async def get_conversation_summary(
    conversation_id: str,
    regenerate: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get or generate conversation summary"""
    service = ConversationService(db)
    
    # Check conversation exists
    conversation = service.get_conversation(conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Get or generate summary
    if regenerate or not conversation.summary:
        summary = await service.generate_conversation_summary(conversation_id)
    else:
        summary = conversation.summary
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not available"
        )
    
    return summary