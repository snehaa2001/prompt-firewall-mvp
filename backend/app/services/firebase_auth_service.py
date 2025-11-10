import firebase_admin
from firebase_admin import auth as firebase_auth
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict

if not firebase_admin._apps:
    firebase_admin.initialize_app()

security = HTTPBearer(auto_error=False)


async def verify_firebase_token(creds: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Dict[str, str]:
    if not creds:
        raise HTTPException(
            status_code=401,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = creds.credentials

    try:
        decoded_token = firebase_auth.verify_id_token(token)
        uid = decoded_token["uid"]
        email = decoded_token.get("email", "")

        user = firebase_auth.get_user(uid)
        role = user.custom_claims.get("role", "user") if user.custom_claims else "user"
        tenant_id = user.custom_claims.get("tenantId", "default") if user.custom_claims else "default"

        return {"uid": uid, "email": email, "role": role, "tenantId": tenant_id}

    except firebase_auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except firebase_auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=401,
            detail="Authentication token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_admin(user: Dict = Depends(verify_firebase_token)) -> Dict:
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


async def create_admin_user(email: str, password: str) -> str:
    user = firebase_auth.create_user(email=email, password=password, email_verified=True)
    firebase_auth.set_custom_user_claims(user.uid, {"role": "admin"})
    return user.uid
