from pydantic import BaseModel, EmailStr
from typing import Optional

# ✅ Schema for user registration
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

# ✅ Schema for user stored in DB
class UserInDB(BaseModel):
    id: Optional[str] = None
    name: str
    email: EmailStr
    hashed_password: str

# ✅ Schema for user login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# ✅ Schema for updating user profile (name & email)
class UserUpdate(BaseModel):
    name: str
    email: EmailStr

# ✅ Schema for changing password
class UserPasswordUpdate(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str
