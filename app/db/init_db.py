from sqlalchemy.orm import Session
from app.models.user import User, PlanType
from app.core.security import get_password_hash
from app.db.session import Base, engine


def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
    print("✓ All tables created")


def init_db(db: Session) -> None:
    """Initialize database with default data"""
    
    # Create tables first
    create_tables()
    
    # Create default admin user
    admin = db.query(User).filter(User.email == "admin@contentgen.com").first()
    
    if not admin:
        admin = User(
            email="admin@contentgen.com",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            is_active=True,
            is_verified=True,
            plan_type=PlanType.ENTERPRISE,
            monthly_quota=999999
        )
        db.add(admin)
        db.commit()
        print("✓ Admin user created")
    
    print("✓ Database initialized")