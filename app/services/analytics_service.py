from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.usage import UsageLog
from app.models.user import User
from datetime import datetime, timedelta


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
    
    def log_usage(
        self,
        user_id: int,
        endpoint: str,
        content_type: Optional[str],
        ai_model: str,  # Changed from model_used
        tokens_used: int,
        cost: float,
        credits_used: int,
        response_time: float,
        status_code: int,
        extra_data: Dict[str, Any] = None  # Changed from metadata
    ) -> UsageLog:
        """Log API usage"""
        log = UsageLog(
            user_id=user_id,
            endpoint=endpoint,
            content_type=content_type,
            ai_model=ai_model,  # Changed
            tokens_used=tokens_used,
            cost=cost,
            credits_used=credits_used,
            response_time=response_time,
            status_code=status_code,
            extra_data=extra_data or {}  # Changed
        )
        
        self.db.add(log)
        
        # Update user quota
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.used_quota += credits_used
        
        self.db.commit()
        return log
    
    def get_user_stats(
        self,
        user_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get user usage statistics"""
        since = datetime.utcnow() - timedelta(days=days)
        
        logs = self.db.query(UsageLog).filter(
            UsageLog.user_id == user_id,
            UsageLog.created_at >= since
        ).all()
        
        total_requests = len(logs)
        total_tokens = sum(log.tokens_used for log in logs)
        total_cost = sum(log.cost for log in logs)
        total_credits = sum(log.credits_used for log in logs)
        
        # Average response time
        avg_response_time = (
            sum(log.response_time for log in logs if log.response_time) / total_requests
            if total_requests > 0 else 0
        )
        
        # Most used models
        model_usage = {}
        for log in logs:
            model_usage[log.ai_model] = model_usage.get(log.ai_model, 0) + 1  # Changed
        
        # Most used content types
        content_type_usage = {}
        for log in logs:
            if log.content_type:
                content_type_usage[log.content_type] = content_type_usage.get(log.content_type, 0) + 1
        
        return {
            "period_days": days,
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 4),
            "total_credits": total_credits,
            "avg_response_time": round(avg_response_time, 2),
            "model_usage": model_usage,
            "content_type_usage": content_type_usage
        }
    
    def get_quota_status(self, user_id: int) -> Dict[str, Any]:
        """Get user's quota status"""
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return {}
        
        remaining = max(0, user.monthly_quota - user.used_quota)
        percentage_used = (user.used_quota / user.monthly_quota * 100) if user.monthly_quota > 0 else 0
        
        return {
            "plan_type": user.plan_type,
            "monthly_quota": user.monthly_quota,
            "used_quota": user.used_quota,
            "remaining_quota": remaining,
            "percentage_used": round(percentage_used, 2)
        }