from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class ContentType(str, Enum):
    BLOG = "blog"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"
    PRODUCT_DESCRIPTION = "product_description"
    YOUTUBE_SCRIPT = "youtube_script"
    RESUME = "resume"
    TRANSLATION = "translation"
    REWRITE = "rewrite"
    SUMMARIZE = "summarize"
    SEO = "seo"


class ToneType(str, Enum):
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    FORMAL = "formal"
    TECHNICAL = "technical"
    CONVERSATIONAL = "conversational"


class LengthType(str, Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class ContentRequest(BaseModel):
    content_type: ContentType
    topic: str
    tone: Optional[ToneType] = ToneType.PROFESSIONAL
    length: Optional[LengthType] = LengthType.MEDIUM
    keywords: Optional[List[str]] = []
    additional_context: Optional[Dict[str, Any]] = {}
    use_memory: bool = True
    session_id: Optional[str] = None
    model: Optional[str] = Field(
        default="gpt-4o-mini",  # ✅ Changed from None to valid model
        description="OpenAI model to use for content generation",
        examples=["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "content_type": "blog",
                "topic": "The future of artificial intelligence in healthcare",
                "tone": "professional",
                "length": "medium",
                "keywords": ["AI", "healthcare", "innovation"],
                "additional_context": {},
                "use_memory": True,
                "session_id": None,
                "model": "gpt-4o-mini"  # ✅ Valid example
            }
        }


class BlogRequest(BaseModel):
    topic: str
    tone: ToneType = ToneType.PROFESSIONAL
    length: LengthType = LengthType.MEDIUM
    keywords: List[str] = []
    include_outline: bool = True
    use_memory: bool = True


class SocialMediaRequest(BaseModel):
    platform: str  # linkedin, twitter, instagram, facebook
    topic: str
    with_hashtags: bool = True
    with_emoji: bool = False
    post_count: int = 1


class EmailRequest(BaseModel):
    email_type: str  # cold_outreach, newsletter, promotional
    subject_lines: int = 3
    audience: str
    cta: Optional[str] = None


class ProductRequest(BaseModel):
    product_name: str
    features: List[str]
    target_audience: str
    length: int = 150  # word count


class ContentResponse(BaseModel):
    content: str
    tokens_used: int
    model_used: str
    context_applied: Optional[Dict[str, Any]] = {}
    suggestions: Optional[List[str]] = []
    metadata: Dict[str, Any] = {}


class BatchContentRequest(BaseModel):
    requests: List[ContentRequest]
    webhook_url: Optional[str] = None
    priority: str = "normal"


class BatchContentResponse(BaseModel):
    batch_id: str
    status: str
    total_requests: int
    estimated_completion: Optional[str] = None