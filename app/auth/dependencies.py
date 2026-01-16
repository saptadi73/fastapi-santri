from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.users.models import User

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user = db.query(User).get(payload["sub"])
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid authentication credentials: {str(e)}")

def require_roles(*roles):
    def guard(user=Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403)
        return user
    return guard
