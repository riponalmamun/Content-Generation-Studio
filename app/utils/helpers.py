from typing import Optional, Dict, Any
import json
from datetime import datetime


def generate_conversation_title(first_message: str, max_length: int = 50) -> str:
    """Generate conversation title from first message"""
    title = first_message[:max_length]
    if len(first_message) > max_length:
        title += "..."
    return title


def calculate_credits(model: str, tokens: int) -> int:
    """Calculate credits based on model and tokens"""
    # Credit calculation logic
    credit_rates = {
        "gpt-4o": 10,
        "gpt-4o-mini": 2,
        "gpt-3.5-turbo": 1
    }
    
    base_credits = credit_rates.get(model, 1)
    # 1 credit per ~100 tokens
    return max(1, base_credits * (tokens // 100))


def calculate_cost(model: str, tokens: int) -> float:
    """Calculate cost in USD based on model and tokens"""
    # OpenAI pricing (approximate)
    cost_per_1k = {
        "gpt-4o": 0.06,  # Combined input + output
        "gpt-4o-mini": 0.001,
        "gpt-3.5-turbo": 0.002
    }
    
    rate = cost_per_1k.get(model, 0.002)
    return (tokens / 1000) * rate


def safe_json_loads(data: str, default: Any = None) -> Any:
    """Safely load JSON with fallback"""
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default or {}


def format_datetime(dt: Optional[datetime]) -> Optional[str]:
    """Format datetime to ISO string"""
    if dt:
        return dt.isoformat()
    return None


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text with suffix"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_keywords(text: str, max_keywords: int = 10) -> list:
    """Extract keywords from text (simple implementation)"""
    # Remove common stop words and extract unique words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
    words = text.lower().split()
    keywords = [w for w in words if w not in stop_words and len(w) > 3]
    return list(set(keywords))[:max_keywords]