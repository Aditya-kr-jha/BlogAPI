from datetime import datetime, timezone
from typing import Optional, List

from fastapi.params import Depends

from sqlmodel import Field, SQLModel, select, Session,Relationship

from .database import engine, get_session
from .models_enums import UserRole, UserStatus

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    first_name: str
    last_name: str
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    role: UserRole = Field(default=UserRole.reader)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: UserStatus = Field(default=UserStatus.active)
    posts: List["Post"] = Relationship(back_populates="user")  # Relationship to Post model
    comments: List["Comment"] = Relationship(back_populates="user")  # Relationship to Comment model
    
class Post(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    author_id: int = Field(foreign_key="user.id")
    created_at:Optional[datetime] = None
    updated_at: Optional[datetime] = None
    view_count: Optional[int] = 0
    is_featured: bool = False
    allow_comments: bool = True
    likes_count: Optional[int] = 0
    user: Optional["User"] =  Relationship(back_populates="posts")
    comments:List["Comment"]=Relationship(back_populates="post")


class Comment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="post.id")
    user_id: int = Field(foreign_key="user.id")
    parent_id: Optional[int] = Field(default=None, foreign_key="comment.id")
    content: str
    created_at: Optional[datetime] = None
    likes_count: Optional[int] = 0
    post: Optional["Post"] = Relationship(back_populates="comments")
    user: Optional["User"] = Relationship(back_populates="comments")

    # Self-referential relationships
    parent: Optional["Comment"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={
            "primaryjoin": "Comment.parent_id == Comment.id",
            "remote_side": "Comment.id"
        }
    )
    children: List["Comment"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={
            "primaryjoin": "Comment.id == Comment.parent_id"
            # remote_side not needed for one-to-many
        }
    )

def get_user(username: str, session) -> Optional[User]:
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    return user
