from fastapi import APIRouter, HTTPException, status, Depends
from typing import Annotated
from sqlalchemy.orm import Session

import models
from database import get_db
from schemas import PostCreate, PostUpdate, PostResponse
from auth import get_current_user


router = APIRouter()


# =========================
# CREATE POST
# =========================

@router.post(
    "/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED
)
def create_post(
    post: PostCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: models.User = Depends(get_current_user)
):

    new_post = models.Post(
        title=post.title,
        content=post.content,
        author_id=current_user.id
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


# =========================
# GET POSTS
# =========================

@router.get(
    "/posts",
    response_model=list[PostResponse]
)
def get_posts(
    db: Annotated[Session, Depends(get_db)],
    skip: int = 0,
    limit: int = 10
):

    posts = db.query(models.Post).offset(skip).limit(limit).all()

    return posts


# =========================
# GET ONE POST
# =========================

@router.get(
    "/posts/{post_id}",
    response_model=PostResponse
)
def get_post(
    post_id: int,
    db: Annotated[Session, Depends(get_db)]
):

    post = db.query(models.Post).filter(
        models.Post.id == post_id
    ).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    return post


# =========================
# UPDATE POST
# =========================

@router.patch(
    "/posts/{post_id}",
    response_model=PostResponse
)
def update_post(
    post_id: int,
    post: PostUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: models.User = Depends(get_current_user)
):

    existing_post = db.query(models.Post).filter(
        models.Post.id == post_id
    ).first()

    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    # Check ownership
    if existing_post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to modify this post"
        )

    if post.title is not None:
        existing_post.title = post.title

    if post.content is not None:
        existing_post.content = post.content

    db.commit()
    db.refresh(existing_post)

    return existing_post


# =========================
# DELETE POST
# =========================

@router.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: models.User = Depends(get_current_user)
):

    post = db.query(models.Post).filter(
        models.Post.id == post_id
    ).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    # Check ownership
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to delete this post"
        )

    db.delete(post)
    db.commit()

    return {
        "message": "Post deleted successfully"
    }