import uuid
from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, Field, EmailStr, IPvAnyAddress, model_validator

from src.schemas import BaseResponseBody


class UserBase(BaseModel):
    id: UUID4 = Field(..., examples=[uuid.uuid4()])
    full_name: str | None = Field(..., examples=["George Lucas"])
    email: EmailStr = Field(..., examples=["j7cZQ@example.com"])
    username: str = Field(..., examples=["george799"])
    created_at: datetime = Field(..., examples=["2032-04-23T10:20:30.400+02:30"])
    updated_at: datetime | None = Field(..., examples=["2032-04-23T10:20:30.400+02:30"])
    last_login: datetime | None = Field(..., examples=["2032-04-23T10:20:30.400+02:30"])

    class Config:
        from_attributes = True


class UserChange(BaseModel):
    full_name: Optional[str] = Field(default=None, examples=["George Lucas"])
    email: Optional[EmailStr] = Field(default=None, examples=["j7cZQ@example.com"])
    username: Optional[str] = Field(default=None, examples=["george799"])
    old_password: Optional[str] = Field(default=None, examples=["12345678"])
    password: Optional[str] = Field(default=None, examples=["12345678"])
    repeat_password: Optional[str] = Field(default=None, examples=["12345678"])

    @model_validator(mode="after")
    def validate_params(self) -> "UserChange":
        if self.password:
            if not self.old_password:
                raise ValueError("You should provide your previous password for changing password")
            if self.password != self.repeat_password:
                raise ValueError("Passwords do not match")
        return self


class UserLogin(BaseModel):
    user_id: UUID4 = Field(..., examples=[uuid.uuid4()])
    date: str = Field(..., examples=["2022-01-01T00:00:00+00:00"])
    ip: IPvAnyAddress = Field(..., examples=["1.0.0.1"])
    user_agent: str = Field(
        ...,
        examples=[
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/100.0.4896.127 Safari/537.36"
        ],
    )


class SingleUserResponse(BaseResponseBody):
    data: UserBase | dict


class SeveralLoginsResponse(BaseResponseBody):
    data: list[UserLogin]
