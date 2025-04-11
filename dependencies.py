from fastapi import Request
from jose import jwt, JWTError
from config import JWT_SECRET_KEY, JWT_ALGORITHM
from database import get_user_by_email

async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        email = payload.get("sub")
        if not email:
            return None
        user = await get_user_by_email(email)
        return user
    except JWTError:
        return None
