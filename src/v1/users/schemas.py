import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import UUID4, BaseModel, Field, EmailStr, IPvAnyAddress, model_validator, ConfigDict

from src.schemas import BaseResponseBody

# from src.v1.roles.schemas import RoleBase


class UserBase(BaseModel):
    model_config: ConfigDict = ConfigDict(from_attributes=True)

    id: UUID4 = Field(..., examples=[uuid.uuid4()])
    full_name: str | None = Field(..., examples=["George Lucas"])
    email: EmailStr = Field(..., examples=["j7cZQ@example.com"])
    username: str = Field(..., examples=["george799"])
    created_at: datetime = Field(..., examples=["2032-04-23T10:20:30.400+02:30"])
    updated_at: datetime | None = Field(..., examples=["2032-04-23T10:20:30.400+02:30"])
    last_login: datetime | None = Field(..., examples=["2032-04-23T10:20:30.400+02:30"])
    # ToDo: add roles after implementing roles
    # roles: Optional[List[RoleBase]] = Field(default=[], examples=[{"id": 1, "name": "Administrator"}])


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, examples=["George Lucas"])
    email: Optional[EmailStr] = Field(default=None, examples=["j7cZQ@example.com"])
    username: Optional[str] = Field(default=None, examples=["george799"])
    current_password: str = Field(..., examples=["12345678"])
    password: Optional[str] = Field(default=None, examples=["12345678"])
    repeat_password: Optional[str] = Field(default=None, examples=["12345678"])

    @model_validator(mode="after")
    def validate_params(self) -> "UserUpdate":
        if self.password:
            if self.password != self.repeat_password:
                raise ValueError("Passwords do not match")
        return self


class UserLoginSchema(BaseModel):
    model_config: ConfigDict = ConfigDict(from_attributes=True)

    user_id: UUID4 = Field(..., examples=[uuid.uuid4()])
    created_at: datetime = Field(..., examples=["2032-04-23T10:20:30.400+02:30"])
    updated_at: datetime | None = Field(..., examples=["2032-04-23T10:20:30.400+02:30"])
    ip: IPvAnyAddress = Field(..., examples=["1.0.0.1"])
    user_agent: str = Field(
        ...,
        examples=[
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/100.0.4896.127 Safari/537.36"
        ],
    )


class UserResponse(BaseResponseBody):
    data: UserBase | dict


class UserLoginsResponse(BaseResponseBody):
    data: list[UserLoginSchema]
