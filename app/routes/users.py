from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from sqlmodel import select

from app.auth import hash_password, get_current_active_user
from app.database import get_session
from app.models import User
from app.models_enums import UserRole, UserStatus
from app.schemas import UserCreate, UserSchema, UserUpdate

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.get(
    "/list_users", status_code=status.HTTP_200_OK, response_model=List[UserSchema]
)
async def list_users(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    List all users in the database.
    """
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized to view users")
    users = db.exec(select(User)).all()
    print(users)
    return users


@user_router.post("/", response_model=UserSchema, status_code=201)
async def create_user(user_dict: UserCreate, db: Session = Depends(get_session)):
    """
    Create a new user in the database.
    """
    existing_user = db.exec(
        select(User).where(User.username == user_dict.username)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = hash_password(user_dict.password)
    # Check if the email already exists
    existing_email = db.exec(select(User).where(User.email == user_dict.email)).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    created_at = datetime.now(timezone.utc)
    updated_at = datetime.now(timezone.utc)
    user = User(
        username=user_dict.username,
        email=user_dict.email,
        hashed_password=hashed_password,
        first_name=user_dict.first_name,
        last_name=user_dict.last_name,
        bio=user_dict.bio,
        profile_picture=user_dict.profile_picture,
        role=UserRole(user_dict.role),
        created_at=updated_at,
        updated_at=updated_at,
        status=UserStatus(user_dict.status),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@user_router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a user by ID.
    """
    user = db.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_dict: UserUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a user's information.
    """
    user = db.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.username != current_user.username:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this user"
        )

    user.username = user_dict.username if user_dict.username else user.username
    user.email = user_dict.email if user_dict.email else user.email
    user.first_name = user_dict.first_name if user_dict.first_name else user.first_name
    user.last_name = user_dict.last_name if user_dict.last_name else user.last_name
    user.bio = user_dict.bio if user_dict.bio is not None else user.bio
    user.profile_picture = (
        user_dict.profile_picture
        if user_dict.profile_picture is not None
        else user.profile_picture
    )
    user.role = UserRole(user_dict.role) if user_dict.role else user.role
    db.commit()
    db.refresh(user)
    return user


@user_router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    # Retrieve the user from the database.
    user = db.exec(select(User).where(User.id == user_id)).first()
    print("user", user)
    print("current_user", current_user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Verify that the current user has the necessary rights.
    if not (
        current_user.role == UserRole.admin or user.username == current_user.username
    ):
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this user"
        )

    # Delete the user and commit the change.
    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}
