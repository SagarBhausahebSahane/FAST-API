from slowapi.util import get_remote_address
from fastapi import Request
from jose import jwt, JWTError
from app.core.config.config import settings

def get_rate_limit_key(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        ip = get_remote_address(request)
        return f"ip:{ip}"
    try:
        payload = jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id:
            return f"user:{user_id}"
        else:
            ip = get_remote_address(request)
            return f"ip:{ip}"
    except JWTError as e:
        ip = get_remote_address(request)
        return f"ip:{ip}"