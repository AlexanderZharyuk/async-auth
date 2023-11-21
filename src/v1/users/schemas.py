import uuid
from typing import Optional
from datetime import datetime
from pydantic import UUID4, BaseModel, Field, model_validator

from src.schemas import BaseResponseBody


class UserBase(BaseModel):
    id: UUID4 = Field(..., examples=[uuid.uuid4()])
    full_name: str | None = Field(..., examples=["George Lucas"])
    email: str = Field(..., examples=["j7cZQ@example.com"])
    username: str = Field(..., examples=["george799"])
    created_at: datetime = Field(..., examples=["2032-04-23T10:20:30.400+02:30"])
    updated_at: datetime | None = Field(..., examples=["2032-04-23T10:20:30.400+02:30"])
    last_login: datetime | None = Field(..., examples=["2032-04-23T10:20:30.400+02:30"])

    class Config:
        from_attributes = True


class UserChange(BaseModel):
    full_name: Optional[str] = Field(examples=["George Lucas"])
    email: Optional[str] = Field(examples=["j7cZQ@example.com"])
    username: Optional[str] = Field(examples=["george799"])
    password: Optional[str] = Field(examples=["12345678"])
    new_password: Optional[str] = Field(examples=["12345678"])

    @model_validator(mode="before")
    def validate_params(self, data):
        if not data:
            raise ValueError("You should provide at least one parameter")
        if data.get("new_password") and not data.get("password"):
            raise ValueError("You should provide the old password for changing password")


class UserLogin(BaseModel):
    user_id: UUID4 = Field(..., examples=[uuid.uuid4()])
    date: str = Field(..., examples=["2022-01-01T00:00:00+00:00"])
    ip: str = Field(..., examples=["127.0.0.1"])
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
