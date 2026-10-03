from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os

import models
from database import get_db
SECRET_KEY = os.getenv("SECRET_KEY")


ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=1)

    to_encode.update({
        "exp": expire #the jwt will expire after the 30 mins from now here onwards 
    })

    token = jwt.encode(
        to_encode, #jwt encode will put it in token and then just sign it
        SECRET_KEY,
        algorithm=ALGORITHM #this block will check the expiration validation no need to add more blocks which will check if the token that is to be expired is there or not 
    )

    return token


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)]
):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY, #no need to check if the token is valid aftetr a certain amount of timme or not here this block catches and raises an exception of invalid jwt
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        user = db.query(models.User).filter(
            models.User.id == int(user_id)
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        return user

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )