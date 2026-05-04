import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    email: EmailStr = Field(max_length=255)


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=30)


class UserResponse(UserBase):
    id: uuid.UUID
