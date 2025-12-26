"""
Import all models here so Alembic can detect them
"""

from app.db.session import Base

# Import all models to register them with SQLAlchemy
from app.models.user import User, APIKey
from app.models.conversation import Conversation, Message, MessageEmbedding, ConversationSummary
from app.models.memory import UserContext
from app.models.usage import UsageLog

# This ensures all models are registered with Base.metadata
__all__ = [
    "Base",
    "User",
    "APIKey", 
    "Conversation",
    "Message",
    "MessageEmbedding",
    "ConversationSummary",
    "UserContext",
    "UsageLog"
]