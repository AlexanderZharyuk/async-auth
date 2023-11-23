from pydantic import BaseModel, Field

from src.schemas import BaseResponseBody


class RoleBase(BaseModel):
    id: int = Field(..., examples=["127856"])
    name: str = Field(..., examples=["Администратор системы."])

    class Config:
        from_attributes = True


class RoleCreate(BaseModel):
    name: str = Field(..., examples=["Администратор системы."])


class RoleModify(BaseModel):
    name_column: str = Field(..., examples=["name"])
    value: str = Field(..., examples=["Moderator"])


class SingleRolesResponse(BaseResponseBody):
    data: RoleBase | dict


class SeveralRolesResponse(BaseResponseBody):
    data: list[RoleBase]