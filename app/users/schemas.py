from pydantic import BaseModel, ConfigDict, EmailStr
from uuid import UUID
from datetime import datetime


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserVerify2FA(BaseModel):
    email: EmailStr
    code: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    email: EmailStr
    code: str
    new_password: str


class FollowedUser(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    followed_at: datetime

    model_config = ConfigDict(from_attributes=True)
