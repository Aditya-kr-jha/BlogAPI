# python
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.auth import get_current_active_user
from app.database import get_session
from app.models import Post, User
from app.models_enums import UserRole
from app.schemas import PostCreate, PostSchema, PostUpdate

post_router = APIRouter(prefix="/posts", tags=["posts"])


@post_router.get(
    "/list_posts", status_code=status.HTTP_200_OK, response_model=List[PostSchema]
)
async def list_posts(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    List all posts in the database.
    """
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized to view posts")
    posts = db.exec(select(Post)).all()
    posts_with_author = []
    for post in posts:
        post_copy = post.model_dump()
        post_copy["author_name"] = post.user.username if post.user else "Unknown"
        posts_with_author.append(post_copy)
    return posts_with_author


@post_router.post("/", response_model=PostSchema, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_active_user),
):
    """
    Create a new post.
    """
    created_at = datetime.now(timezone.utc)
    post = Post(
        title=post_data.title,
        content=post_data.content,
        author_id=current_user.id,
        created_at=created_at,
        updated_at=created_at,
        view_count=post_data.view_count or 0,
        is_featured=(
            post_data.is_featured if post_data.is_featured is not None else False
        ),
        allow_comments=(
            post_data.allow_comments if post_data.allow_comments is not None else True
        ),
        likes_count=post_data.likes_count or 0,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    post_copy = post.model_dump()
    post_copy["author_name"] = current_user.username
    return post_copy


@post_router.get("/{post_id}", response_model=PostSchema)
async def get_post(
    post_id: int,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_active_user),
):
    """
    Retrieve a post by ID.
    """
    post = db.exec(select(Post).where(Post.id == post_id)).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    author_name = post.user.username
    post_copy = post.model_dump()
    post_copy["author_name"] = author_name
    return post_copy


@post_router.put("/{post_id}", response_model=PostSchema)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_active_user),
):
    """
    Update a post.
    """
    post = db.exec(select(Post).where(Post.id == post_id)).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if not (current_user.role == UserRole.admin or post.author_id == current_user.id):
        raise HTTPException(
            status_code=403, detail="Not authorized to update this post"
        )

    post.title = post_data.title if post_data.title else post.title
    post.content = post_data.content if post_data.content else post.content
    post.view_count = (
        post_data.view_count if post_data.view_count is not None else post.view_count
    )
    post.is_featured = (
        post_data.is_featured if post_data.is_featured is not None else post.is_featured
    )
    post.allow_comments = (
        post_data.allow_comments
        if post_data.allow_comments is not None
        else post.allow_comments
    )
    post.likes_count = (
        post_data.likes_count if post_data.likes_count is not None else post.likes_count
    )
    post.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(post)
    post_copy = post.model_dump()
    author_name = post.user.username
    post_copy["author_name"] = author_name
    return post_copy


@post_router.delete("/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post(
    post_id: int,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_active_user),
):
    """
    Delete a post.
    """
    post = db.exec(select(Post).where(Post.id == post_id)).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if not (current_user.role == UserRole.admin or post.author_id == current_user.id):
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this post"
        )

    db.delete(post)
    db.commit()
    return {"detail": "Post deleted successfully"}
