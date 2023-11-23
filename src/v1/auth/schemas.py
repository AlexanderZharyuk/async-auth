from pydantic import UUID4, BaseModel, EmailStr, model_validator


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


class User(UserBase):
    id: UUID4

    class Config:
        from_attributes = True
