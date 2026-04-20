from fastapi import APIRouter, Depends, HTTPException
from app.core.db.db_connection import get_db
from app.models.user.user_model import UserCreate, UserUpdate, EmailList
from app.core.security.auth import hash_password,get_current_user,access_control_auth

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
@access_control_auth("admin")
async def get_users(db=Depends(get_db),current_user:dict= Depends(get_current_user)) -> dict:
    users = await db.users.find({}, {"_id": 0}).to_list()
    if not len(users):
        raise HTTPException(status_code=400,detail="No User Found")
    return {"users": users,"current_user":current_user}

@router.post("/")
@access_control_auth("admin")
async def create_user(db=Depends(get_db), current_user:dict= Depends(get_current_user),user: UserCreate = ...) -> dict:
    user_data = user.dict()
    if await db.users.find_one({"email": user_data['email']}):
        raise HTTPException(status_code=409, detail="User already exists")
    user_data['password'] = hash_password(user_data['password'])
    result = await db.users.insert_one(user_data)
    return {"msg": "User created successfully!", "inserted_id": str(result.inserted_id)}

@router.put("/")
@access_control_auth("admin")
async def update_user(db=Depends(get_db),current_user:dict= Depends(get_current_user), user: UserUpdate = ...) -> dict:
    user_data = user.dict()
    existing = await db.users.find_one({"email": user_data['email']}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")
    if existing == user_data:
        raise HTTPException(status_code=400, detail="No changes detected")
    result =  await db.users.update_one({'email':user['email']},{'$set':{'email':user['email'],'name':user['name'],'age':user['age']}})
    return {"msg": "User updated successfully!", "modified_count": result.modified_count}


@router.delete("/")
@access_control_auth("admin")
async def delete_user(db=Depends(get_db),current_user:dict= Depends(get_current_user),user_emails: EmailList = ...) -> dict:
    user_emails = user_emails.dict()
    delete_users = await db.users.delete_many({"email": {"$in": user_emails['emails']}})
    if delete_users.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No users found")
    
    await db.refresh_tokens.delete_many({"user_email": {"$in": user_emails['emails']}})
    return {"msg": "User deleted successfully!", "deleted_count": delete_users.deleted_count}