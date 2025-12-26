from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user, check_quota
from app.models.user import User
from app.schemas.content import (
    ContentRequest,
    ContentResponse,
    BlogRequest,
    SocialMediaRequest,
    EmailRequest,
    ProductRequest
)
from app.services.openai_service import openai_service
from app.services.memory_service import MemoryService
from app.services.analytics_service import AnalyticsService
from app.utils.helpers import calculate_credits, calculate_cost
from app.utils.rate_limiter import rate_limiter
from datetime import datetime


router = APIRouter()


@router.post("/generate", response_model=ContentResponse)
async def generate_content(
    request: ContentRequest,
    current_user: User = Depends(check_quota),
    db: Session = Depends(get_db)
):
    """Generate content with AI"""
    
    # Rate limiting
    allowed, error_msg = rate_limiter.check_user_rate_limits(
        user_id=current_user.id,
        endpoint="content",
        per_minute=30,
        per_hour=500
    )
    
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=error_msg
        )
    
    memory_service = MemoryService(db)
    analytics_service = AnalyticsService(db)
    
    # Get user context
    user_context = {}
    if request.use_memory:
        user_context = memory_service.get_user_context(current_user.id)
    
    # Track start time
    start_time = datetime.utcnow()
    
    try:
        # Generate content
        result = await openai_service.generate_with_context(
            user_message=request.topic,
            content_type=request.content_type.value,
            user_context=user_context,
            model=request.model
        )
        
        content = result["content"]
        tokens_used = result["tokens_used"]
        model_used = result["model_used"]
        
        # Calculate metrics
        response_time = (datetime.utcnow() - start_time).total_seconds()
        credits_used = calculate_credits(model_used, tokens_used)
        cost = calculate_cost(model_used, tokens_used)
        
        # Log usage - CHANGED PARAMETER NAME
        analytics_service.log_usage(
            user_id=current_user.id,
            endpoint="/content/generate",
            content_type=request.content_type.value,
            ai_model=model_used,  # Changed from model_used
            tokens_used=tokens_used,
            cost=cost,
            credits_used=credits_used,
            response_time=response_time,
            status_code=200
        )
        
        return {
            "content": content,
            "tokens_used": tokens_used,
            "model_used": model_used,
            "context_applied": user_context,
            "suggestions": [],
            "metadata": {
                "credits_used": credits_used,
                "response_time": response_time
            }
        }
    
    except Exception as e:
        response_time = (datetime.utcnow() - start_time).total_seconds()
        analytics_service.log_usage(
            user_id=current_user.id,
            endpoint="/content/generate",
            content_type=request.content_type.value,
            ai_model="unknown",  # Changed
            tokens_used=0,
            cost=0,
            credits_used=0,
            response_time=response_time,
            status_code=500,
            extra_data={"error": str(e)}  # Changed from metadata
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )


@router.post("/blog", response_model=ContentResponse)
async def generate_blog(
    request: BlogRequest,
    current_user: User = Depends(check_quota),
    db: Session = Depends(get_db)
):
    """Generate blog article"""
    
    prompt = f"""
Write a {request.length.value} blog article about: {request.topic}

Tone: {request.tone.value}
Keywords to include: {', '.join(request.keywords) if request.keywords else 'None'}

{"Include an outline at the beginning." if request.include_outline else ""}

Make it engaging, well-structured, and SEO-friendly.
"""
    
    content_request = ContentRequest(
        content_type="blog",
        topic=prompt,
        use_memory=request.use_memory
    )
    
    return await generate_content(content_request, current_user, db)


@router.post("/social-media", response_model=ContentResponse)
async def generate_social_media(
    request: SocialMediaRequest,
    current_user: User = Depends(check_quota),
    db: Session = Depends(get_db)
):
    """Generate social media post"""
    
    prompt = f"""
Create {request.post_count} {request.platform} post(s) about: {request.topic}

{"Include relevant hashtags." if request.with_hashtags else ""}
{"Use appropriate emojis." if request.with_emoji else ""}

Make it engaging and platform-appropriate.
"""
    
    content_request = ContentRequest(
        content_type="social_media",
        topic=prompt,
        use_memory=True
    )
    
    return await generate_content(content_request, current_user, db)


@router.post("/email", response_model=ContentResponse)
async def generate_email(
    request: EmailRequest,
    current_user: User = Depends(check_quota),
    db: Session = Depends(get_db)
):
    """Generate email content"""
    
    prompt = f"""
Create a {request.email_type} email:

Target audience: {request.audience}
Generate {request.subject_lines} subject line options
{"Call-to-action: " + request.cta if request.cta else ""}

Include both subject lines and email body.
"""
    
    content_request = ContentRequest(
        content_type="email",
        topic=prompt,
        use_memory=True
    )
    
    return await generate_content(content_request, current_user, db)


@router.post("/product-description", response_model=ContentResponse)
async def generate_product_description(
    request: ProductRequest,
    current_user: User = Depends(check_quota),
    db: Session = Depends(get_db)
):
    """Generate product description"""
    
    prompt = f"""
Write a compelling product description for: {request.product_name}

Features: {', '.join(request.features)}
Target audience: {request.target_audience}
Length: approximately {request.length} words

Focus on benefits and conversion.
"""
    
    content_request = ContentRequest(
        content_type="product_description",
        topic=prompt,
        use_memory=True
    )
    
    return await generate_content(content_request, current_user, db)