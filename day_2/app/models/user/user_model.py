from pydantic import BaseModel, Field, EmailStr
from typing import Optional,List
from datetime import datetime

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, example="John Doe")
    email: EmailStr = Field(..., example="john@example.com")
    age: int = Field(..., ge=0, le=150, example=25)
    password: str = Field(..., min_length=6,max_length=72,example="secret123")

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    age: Optional[int] = Field(None, ge=0, le=150)

class EmailList(BaseModel):
    emails: List[EmailStr] = Field(..., min_length=1, example=["john@example.com"])

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserUpdatePassword(BaseModel):
    old_password:str
    new_password:str=Field(...,min_length=6)