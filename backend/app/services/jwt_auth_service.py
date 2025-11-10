"""
JWT Authentication Service - Simple self-contained auth for MVP demo/testing
"""
from datetime import datetime, timedelta
from typing import Optional, Dict
import os
from jose import JWTError, jwt

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production-min-32-chars")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# Demo Admin Credentials (hardcoded for MVP - simple comparison for demo purposes)
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@demo.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")


def authenticate_user(email: str, password: str) -> Optional[Dict[str, str]]:
    """
    Authenticate user with email and password
    Returns user info if valid, None otherwise

    Note: For MVP/demo purposes, using simple password comparison.
    In production, use proper password hashing with bcrypt or argon2.
    """
    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        return {
            "email": email,
            "role": "admin",
            "user_id": "admin-001"
        }
    return None


def create_access_token(data: dict) -> str:
    """
    Create a JWT access token

    Args:
        data: Dictionary with user claims (email, role, user_id)

    Returns:
        JWT token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, str]]:
    """
    Verify and decode a JWT token

    Args:
        token: JWT token string

    Returns:
        Dictionary with user info if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            return None
        return {
            "email": email,
            "role": payload.get("role", "user"),
            "user_id": payload.get("user_id", "unknown")
        }
    except JWTError:
        return None
