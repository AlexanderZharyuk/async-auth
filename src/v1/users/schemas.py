from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class SuperUserCreate(BaseModel):
    username: str = Field(...)
    password: str = Field(...)
    repeat_password: str = Field(...)
    full_name: Optional[str] | None = Field(default=None)
    email: Optional[EmailStr] | None = Field(default=None)
