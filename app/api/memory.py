from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.memory import (
    UserContextCreate,
    UserContextUpdate,
    UserContextResponse,
    UserContextSummary,
    ConversationSearchRequest,
    ConversationSearchResponse,
    ConversationSearchResult
)
from app.services.memory_service import MemoryService
from app.services.embedding_service import EmbeddingService


router = APIRouter()


@router.get("/context", response_model=UserContextSummary)
def get_user_context(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's learned context"""
    service = MemoryService(db)
    return service.get_context_summary(current_user.id)


@router.get("/context/all", response_model=List[UserContextResponse])
def get_all_context(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all user context entries"""
    service = MemoryService(db)
    from app.models.memory import UserContext
    
    contexts = db.query(UserContext).filter(
        UserContext.user_id == current_user.id
    ).all()
    
    return contexts


@router.put("/context/{key}", response_model=UserContextResponse)
def update_context(
    key: str,
    data: UserContextUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update specific context"""
    service = MemoryService(db)
    
    context = service.update_or_create_context(
        user_id=current_user.id,
        key=key,
        value=data.value,
        confidence_score=1.0  # Manual update has high confidence
    )
    
    return context


@router.post("/context", response_model=UserContextResponse)
def create_context(
    data: UserContextCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new context"""
    service = MemoryService(db)
    
    # Check if exists
    existing = service.get_context_by_key(current_user.id, data.key)
    if existing and not data.override:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Context key already exists. Use override=true to update."
        )
    
    context = service.update_or_create_context(
        user_id=current_user.id,
        key=data.key,
        value=data.value,
        confidence_score=1.0
    )
    
    return context


@router.delete("/context/{key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_context(
    key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete specific context"""
    service = MemoryService(db)
    
    success = service.delete_context(current_user.id, key)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Context not found"
        )
    
    return None


@router.post("/search", response_model=ConversationSearchResponse)
async def search_conversations(
    search_data: ConversationSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search past conversations semantically"""
    embedding_service = EmbeddingService(db)
    
    # Search similar messages
    results = await embedding_service.search_similar_messages(
        query=search_data.query,
        user_id=current_user.id,
        limit=search_data.limit
    )
    
    # Format results
    search_results = []
    for message, score in results:
        search_results.append(
            ConversationSearchResult(
                conversation_id=message.conversation_id,
                title=message.conversation.title,
                snippet=message.content[:200] + "..." if len(message.content) > 200 else message.content,
                relevance_score=round(score, 3),
                date=message.created_at
            )
        )
    
    return {
        "results": search_results,
        "total": len(search_results)
    }