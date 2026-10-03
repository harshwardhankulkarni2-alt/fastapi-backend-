from pydantic import BaseModel, ConfigDict, Field


# =========================
# POST SCHEMAS
# =========================

class PostCreate(BaseModel):

    title: str = Field(
        min_length=3,
        max_length=100
    )

    content: str = Field(
        min_length=1
    )
  

class PostUpdate(BaseModel):

    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=100
    )

    content: str | None = Field(
        default=None,
        min_length=1
    )


class PostResponse(BaseModel):

    id: int
    title: str
    content: str

    model_config = ConfigDict(
        from_attributes=True
    )


# =========================
# USER SCHEMAS
# =========================

class UserCreate(BaseModel):

    username: str = Field(
        min_length=3,
        max_length=50
    )

    email: str
    password : str = Field(
        min_length=8
    )


class UserResponse(BaseModel):

    id: int
    username: str
    email: str

    model_config = ConfigDict(
        from_attributes=True
    )
class UserLogin(BaseModel):
        username : str
        password : str