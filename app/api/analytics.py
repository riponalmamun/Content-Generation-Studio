from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.analytics_service import AnalyticsService


router = APIRouter()


@router.get("/stats")
def get_usage_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user usage statistics"""
    service = AnalyticsService(db)
    return service.get_user_stats(current_user.id, days)


@router.get("/quota")
def get_quota_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's quota status"""
    service = AnalyticsService(db)
    return service.get_quota_status(current_user.id)