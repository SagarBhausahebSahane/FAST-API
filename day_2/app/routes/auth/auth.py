from fastapi import APIRouter, Depends, HTTPException, Response, Request
from app.core.db.db_connection import get_db
from app.core.security.auth import ( hash_password, verify_password, create_access_token, create_refresh_token, save_refresh_token, rotate_refresh_token,decode_token)
from app.models.user.user_model import UserCreate,UserLogin
from app.middleware.rate_limit_handler.rate_limit_handler import limiter

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
async def register(db=Depends(get_db), user: UserCreate = ...) -> dict:
    user_data = user.dict()
    if await db.users.find_one({"email": user_data['email']}):
        raise HTTPException(status_code=409, detail="User already exists")
    user_data['password'] = hash_password(user_data['password'])
    result = await db.users.insert_one(user_data)
    return {"msg": "Registered successfully!", "inserted_id": str(result.inserted_id)}


@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request,response: Response, db=Depends(get_db), user: UserLogin = ...) -> dict:
    existing = await db.users.find_one({"email": user.email})
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(user.password, existing['password']):
        raise HTTPException(status_code=401, detail="Wrong password")
    access_token = create_access_token(user.email)
    refresh_token = create_refresh_token(user.email)
    await save_refresh_token(db, user.email, refresh_token)
    response.set_cookie(key="access_token",value=access_token,httponly=True,secure=True,max_age=15 * 60)
    response.set_cookie(key="refresh_token",value=refresh_token,httponly=True,secure=True,max_age=7 * 24 * 60 * 60)
    return {"msg": "Logged in successfully!"} 


@router.post("/refresh")
async def refresh(request: Request, response: Response, db=Depends(get_db)) -> dict:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    tokens = await rotate_refresh_token(db, refresh_token)
    response.set_cookie( key="access_token", value=tokens['access_token'], httponly=True, secure=True, max_age=15 * 60)
    response.set_cookie( key="refresh_token", value=tokens['refresh_token'], httponly=True, secure=True, max_age=7 * 24 * 60 * 60)
    return {"msg": "Token refreshed!"}


@router.post("/logout")
async def logout(request: Request, response: Response, db=Depends(get_db)) -> dict:
    refresh_token = request.cookies.get("refresh_token")
    access_token = request.cookies.get("access_token")
    if not refresh_token and not access_token:
        raise HTTPException(status_code=401, detail="Already logged out")
    email = decode_token(access_token) if access_token else None
    if email:
        await db.refresh_tokens.delete_many({"user_email": email})
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return {"msg": "Logged out successfully!"}