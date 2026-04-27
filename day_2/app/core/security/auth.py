from datetime import datetime, timedelta, UTC
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException,Request
from fastapi.security import OAuth2PasswordBearer
from app.core.config.config import settings
from functools import wraps

pwd_context = CryptContext(schemes=["bcrypt"])


# ====== Password ======
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(email: str,role:str="normal") -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": email, "exp": expire, "type": "access","role":role},settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(email: str) -> str:
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return jwt.encode({"sub": email, "exp": expire, "type": "refresh"},settings.REFRESH_SECRET_KEY,algorithm=settings.ALGORITHM)

async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        email = payload.get("sub")
        role = payload.get("role")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"email": email, "role": role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expired or invalid")

def decode_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

async def save_refresh_token(db, email: str, token: str):
    expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    await db.refresh_tokens.delete_many({"user_email": email})
    await db.refresh_tokens.insert_one({"user_email": email,"token": token,"expires_at": expires_at,"is_revoked": False})

async def rotate_refresh_token(db, old_token: str) -> dict:
    stored = await db.refresh_tokens.find_one({"token": old_token})
    if not stored:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    user = await db.users.find_one({"email": stored['user_email']})
    if not user:
        await db.refresh_tokens.delete_many({"user_email": stored['user_email']})
        raise HTTPException(status_code=401, detail="User no longer exists")

    if stored['is_revoked']:
        await db.refresh_tokens.update_many({"user_email": stored['user_email']},{"$set": {"is_revoked": True}})
        raise HTTPException(status_code=401,detail="Token reuse detected! All sessions logged out.")

    if stored['expires_at'].replace(tzinfo=UTC) < datetime.now(UTC):
        raise HTTPException(status_code=401, detail="Refresh token expired")

    await db.refresh_tokens.update_one({"token": old_token},{"$set": {"is_revoked": True}})

    email = stored['user_email']
    new_refresh_token = create_refresh_token(email)
    new_access_token = create_access_token(email)

    await db.refresh_tokens.insert_one({"user_email": email,"token": new_refresh_token,"expires_at": datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),"is_revoked": False})

    return {"access_token": new_access_token,"refresh_token": new_refresh_token}


# @wraps yeh sab copy karta hai:
# ┌──────────────────┬──────────────────────────────┐
# │ Attribute        │ Example                      │
# ├──────────────────┼──────────────────────────────┤
# │ __name__         │ "admin_route"                │
# │ __doc__          │ "Yeh admin ka route hai"     │
# │ __module__       │ "app.routes.user.user_route" │
# │ __qualname__     │ "admin_route"                │
# │ __annotations__  │ return type hints            │
# │ __dict__         │ extra attributes             │
# └──────────────────┴──────────────────────────────┘

def access_control_auth(*roles):
    def decorator(func):
        @wraps(func)
        async def wrapper(**kwargs):
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(status_code=401, detail="Not authenticated")
            if current_user['role'] not in roles:
                raise HTTPException(status_code=403, detail="Not authorized")
            return await func(**kwargs)
        return wrapper
    return decorator