from fastapi import APIRouter, HTTPException, status, Depends
from typing import Annotated
from sqlalchemy.orm import Session

import models
from database import get_db
from schemas import UserCreate, UserResponse, UserLogin
from pwdlib import PasswordHash
from auth import create_access_token , get_current_user
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter()

pwd_hasher = PasswordHash.recommended()


# =========================
# CREATE USER
# =========================

@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(
    user: UserCreate,
    db: Annotated[Session, Depends(get_db)]

):

    existing_user = db.query(models.User).filter(
        (models.User.username == user.username) |
        (models.User.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists"
        )

    new_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=pwd_hasher.hash(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# =========================
# GET ONE USER
# =========================

@router.get(
    "/users/{user_id}",
    response_model=UserResponse
)
def get_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)]
):

    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


# =========================
# LOGIN
# =========================
@router.post("/login")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)]
):

    existing_user = db.query(models.User).filter(
        models.User.username == form_data.username
    ).first()

    print("USERNAME:", form_data.username)
    print("USER:", existing_user)
    print("PASSWORD ENTERED:", form_data.password)
    print("HASH:", existing_user.password_hash if existing_user else None)

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    password_correct = pwd_hasher.verify(
        form_data.password,
        existing_user.password_hash
    )

    print("PASSWORD CORRECT:", password_correct)

    if not password_correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    access_token = create_access_token(
        {
            "sub": str(existing_user.id)
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/protected")
def protected_route(
    current_user: models.User = Depends(get_current_user)
):
    return {
        "message": "You are authenticated!",
        "username": current_user.username,
        "user_id": current_user.id
    }