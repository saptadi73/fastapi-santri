from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.users.models import User


def get_current_user(
    token: str = Depends(lambda: None),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user = db.query(User).get(payload["sub"])
        if not user:
            raise HTTPException(401)
        return user
    except JWTError:
        raise HTTPException(401)

def require_roles(*roles):
    def guard(user=Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403)
        return user
    return guard
