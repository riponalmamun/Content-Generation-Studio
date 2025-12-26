from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets
import hashlib

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ==================== Password Functions ====================
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


# ==================== JWT Token Functions ====================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        print(f"❌ JWT Decode Error: {e}")  # Debugging জন্য
        return None


# ==================== API Key Functions ====================
def generate_api_key() -> str:
    """
    Generate secure API key with format: cgs_<64 hex characters>
    Example: cgs_a1b2c3d4e5f6...
    """
    random_part = secrets.token_hex(32)  # 32 bytes = 64 hex chars
    return f"cgs_{random_part}"


def hash_api_key(api_key: str) -> str:
    """
    Hash API key using SHA-256 (NOT bcrypt)
    
    Why SHA-256 instead of bcrypt?
    - We need to extract prefix from the key for database lookup
    - Bcrypt would make the hash completely different each time
    - SHA-256 is deterministic and secure for this use case
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """
    Verify API key against its hash
    
    This is a simple comparison since SHA-256 is deterministic
    """
    return hash_api_key(plain_key) == hashed_key


def get_api_key_prefix(api_key: str) -> str:
    """
    Extract prefix from API key for database indexing
    Format: cgs_ + first 8 characters = 12 total
    
    Example: 
    - Full key: cgs_a1b2c3d4e5f6g7h8...
    - Prefix:   cgs_a1b2c3d4
    """
    if not api_key.startswith("cgs_"):
        raise ValueError("Invalid API key format - must start with 'cgs_'")
    
    return api_key[:12]  # cgs_ (4 chars) + 8 chars = 12