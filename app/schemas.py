from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models_enums import UserRole, UserStatus


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserSchema(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    first_name: str
    last_name: str
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    role: UserRole
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: UserStatus

    class Config:
        from_attributes = True


class UserCreate(UserSchema):
    password: str


class UserUpdate(BaseModel):
    username: str = None
    email: str = None
    first_name: str = None
    last_name: str = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    role: Optional[UserRole] = None

    class Config:
        from_attributes = True


class PostCreate(BaseModel):
    title: str
    content: str
    view_count: Optional[int] = 0
    is_featured: Optional[bool] = False
    allow_comments: Optional[bool] = True
    likes_count: Optional[int] = 0


class PostSchema(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    author_name: str
    created_at: datetime
    updated_at: datetime
    view_count: int
    is_featured: bool
    allow_comments: bool
    likes_count: int

    class Config:
        from_attributes = True


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    view_count: Optional[int] = None
    is_featured: Optional[bool] = None
    allow_comments: Optional[bool] = None
    likes_count: Optional[int] = None
