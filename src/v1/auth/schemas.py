from pydantic import UUID4, BaseModel, EmailStr, model_validator

from src.schemas import BaseResponseBody


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str
    repeat_password: str

    @model_validator(mode="after")
    def check_passwords_match(self) -> "UserCreate":
        if self.password is not None and self.repeat_password is not None:
            if self.password != self.repeat_password:
                raise ValueError("Passwords do not match")
        return self


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserLogout(BaseModel):
    refresh_token: str


class User(UserBase):
    id: UUID4

    class Config:
        from_attributes = True


class UserResponse(BaseResponseBody):
    data: User


class JWTTokens(BaseModel):
    access_token: str
    refresh_token: str


class TokensResponse(BaseResponseBody):
    data: JWTTokens


class LogoutResponse(BaseResponseBody):
    data: dict = {"sucess": True}
