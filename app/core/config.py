from pydantic_settings import BaseSettings
from typing import Optional, List
import secrets


class Settings(BaseSettings):
    # ==================== Application ====================
    APP_NAME: str = "Content Generation Studio"
    DEBUG: bool = True  # Development এ True রাখুন
    API_V1_STR: str = "/api"
    
    # Security - Development এর জন্য default value দিয়ে রাখলাম
    # Production এ অবশ্যই .env থেকে load করবেন
    SECRET_KEY: str = secrets.token_urlsafe(32)
    
    # ==================== Database ====================
    DATABASE_URL: str = "sqlite:///./content_studio.db"
    
    # ==================== OpenAI ====================
    OPENAI_API_KEY: Optional[str] = None  # Optional করলাম startup error এড়াতে
    
    # ==================== Redis ====================
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = False  # Development এ False রাখুন
    
    # ==================== JWT ====================
    JWT_SECRET_KEY: str = secrets.token_urlsafe(32)  # Auto-generate for dev
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # ==================== CORS ====================
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    # ==================== Rate Limiting ====================
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    RATE_LIMIT_ENABLED: bool = True
    
    # ==================== OpenAI Models ====================
    DEFAULT_MODEL: str = "gpt-4o-mini"
    PREMIUM_MODEL: str = "gpt-4o"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Model costs (per 1K tokens)
    GPT4O_MINI_INPUT_COST: float = 0.00015
    GPT4O_MINI_OUTPUT_COST: float = 0.0006
    GPT4O_INPUT_COST: float = 0.0025
    GPT4O_OUTPUT_COST: float = 0.01
    
    # ==================== Quotas ====================
    # Credits per month (1 credit ≈ 1 API call)
    FREE_TIER_CREDITS: int = 100
    BASIC_TIER_CREDITS: int = 1000
    PRO_TIER_CREDITS: int = 10000
    ENTERPRISE_TIER_CREDITS: int = 100000
    
    # ==================== Context Memory ====================
    MAX_CONTEXT_MESSAGES: int = 20  # Maximum messages to keep in context
    SIMILARITY_THRESHOLD: float = 0.7  # For semantic search
    
    # ==================== File Upload ====================
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_FILE_TYPES: List[str] = [".txt", ".pdf", ".doc", ".docx", ".md"]
    
    # ==================== Logging ====================
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env


# Create settings instance
settings = Settings()


# Validation function (optional but recommended)
def validate_settings():
    """Validate critical settings on startup"""
    errors = []
    
    if settings.DEBUG:
        print("⚠️  Running in DEBUG mode")
    
    if not settings.OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY is not set")
    
    if settings.SECRET_KEY == settings.JWT_SECRET_KEY:
        print("⚠️  SECRET_KEY and JWT_SECRET_KEY are the same. Consider using different keys.")
    
    if errors:
        print("\n❌ Configuration Errors:")
        for error in errors:
            print(f"  - {error}")
        print("\n💡 Tip: Check your .env file\n")
    
    return len(errors) == 0


# Auto-validate on import (optional)
if __name__ != "__main__":
    is_valid = validate_settings()