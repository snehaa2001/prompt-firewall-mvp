from typing import Optional
from app.services.jwt_auth_service import verify_token as jwt_verify_token

async def verify_token(authorization: Optional[str]) -> dict:
    """
    Verify JWT token from Authorization header

    Args:
        authorization: Authorization header value (Bearer <token>)

    Returns:
        Dictionary with user info (email, role, user_id)

    Raises:
        ValueError: If token is invalid or missing
    """
    if not authorization:
        raise ValueError("No authorization header provided")

    if not authorization.startswith("Bearer "):
        raise ValueError("Invalid authorization format")

    token = authorization.split("Bearer ")[1]

    try:
        decoded_user = jwt_verify_token(token)
        if not decoded_user:
            raise ValueError("Invalid or expired token")
        return decoded_user
    except Exception as e:
        raise ValueError(f"Invalid token: {str(e)}")
