from typing import Optional, Tuple
import redis
from datetime import datetime, timedelta
from app.core.config import settings


class RateLimiter:
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    def check_rate_limit(
        self,
        key: str,
        limit: int,
        window_seconds: int = 60
    ) -> Tuple[bool, int]:
        """
        Check if rate limit is exceeded
        Returns (is_allowed, remaining_requests)
        """
        try:
            current = self.redis_client.get(key)
            
            if current is None:
                # First request in window
                self.redis_client.setex(key, window_seconds, 1)
                return True, limit - 1
            
            current_count = int(current)
            
            if current_count >= limit:
                return False, 0
            
            # Increment counter
            self.redis_client.incr(key)
            return True, limit - current_count - 1
        except redis.RedisError:
            # If Redis fails, allow the request
            return True, limit
    
    def get_rate_limit_key(
        self,
        user_id: int,
        endpoint: str,
        window: str = "minute"
    ) -> str:
        """Generate rate limit key"""
        timestamp = datetime.utcnow()
        
        if window == "minute":
            time_window = timestamp.strftime("%Y-%m-%d-%H-%M")
        elif window == "hour":
            time_window = timestamp.strftime("%Y-%m-%d-%H")
        else:
            time_window = timestamp.strftime("%Y-%m-%d")
        
        return f"rate_limit:{user_id}:{endpoint}:{window}:{time_window}"
    
    def check_user_rate_limits(
        self,
        user_id: int,
        endpoint: str,
        per_minute: int = 60,
        per_hour: int = 1000
    ) -> Tuple[bool, str]:
        """
        Check both minute and hour rate limits
        Returns (is_allowed, error_message)
        """
        # Check per-minute limit
        minute_key = self.get_rate_limit_key(user_id, endpoint, "minute")
        allowed_minute, remaining_minute = self.check_rate_limit(
            minute_key, per_minute, 60
        )
        
        if not allowed_minute:
            return False, f"Rate limit exceeded: {per_minute} requests per minute"
        
        # Check per-hour limit
        hour_key = self.get_rate_limit_key(user_id, endpoint, "hour")
        allowed_hour, remaining_hour = self.check_rate_limit(
            hour_key, per_hour, 3600
        )
        
        if not allowed_hour:
            return False, f"Rate limit exceeded: {per_hour} requests per hour"
        
        return True, ""
    
    def reset_rate_limit(self, key: str) -> bool:
        """Reset rate limit for a key"""
        try:
            self.redis_client.delete(key)
            return True
        except redis.RedisError:
            return False


rate_limiter = RateLimiter()