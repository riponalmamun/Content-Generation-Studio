from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user, check_quota
from app.models.user import User
from app.schemas.conversation import MessageCreate, MessageResponse
from app.services.conversation_service import ConversationService
from app.services.analytics_service import AnalyticsService
from app.utils.helpers import calculate_credits, calculate_cost
from app.utils.rate_limiter import rate_limiter
from datetime import datetime


router = APIRouter()


@router.post("/{conversation_id}", response_model=dict)
async def send_message(
    conversation_id: str,
    message_data: MessageCreate,
    use_memory: bool = True,
    current_user: User = Depends(check_quota),
    db: Session = Depends(get_db)
):
    """Send message to conversation"""
    
    # Rate limiting
    allowed, error_msg = rate_limiter.check_user_rate_limits(
        user_id=current_user.id,
        endpoint="messages",
        per_minute=60,
        per_hour=1000
    )
    
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=error_msg
        )
    
    service = ConversationService(db)
    analytics_service = AnalyticsService(db)
    
    # Check conversation exists
    conversation = service.get_conversation(conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Track start time
    start_time = datetime.utcnow()
    
    # Process message
    try:
        result = await service.chat_with_memory(
            user_id=current_user.id,
            message=message_data.content,
            conversation_id=conversation_id,
            use_memory=use_memory
        )
        
        # Calculate response time
        response_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Log usage - CHANGED PARAMETER NAME
        analytics_service.log_usage(
            user_id=current_user.id,
            endpoint="/messages",
            content_type="conversation",
            ai_model=result["model_used"],  # Changed
            tokens_used=result["tokens_used"],
            cost=calculate_cost(result["model_used"], result["tokens_used"]),
            credits_used=result["credits_used"],
            response_time=response_time,
            status_code=200
        )
        
        return result
    
    except Exception as e:
        # Log error
        response_time = (datetime.utcnow() - start_time).total_seconds()
        analytics_service.log_usage(
            user_id=current_user.id,
            endpoint="/messages",
            content_type="conversation",
            ai_model="unknown",  # Changed
            tokens_used=0,
            cost=0,
            credits_used=0,
            response_time=response_time,
            status_code=500,
            extra_data={"error": str(e)}  # Changed
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Message processing failed: {str(e)}"
        )