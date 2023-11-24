from pydantic import BaseModel, Field

from src.schemas import BaseResponseBody


class RoleBase(BaseModel):
    id: int = Field(..., examples=["127856"])
    name: str = Field(..., examples=["Администратор системы."])

    class Config:
        from_attributes = True


class RoleCreate(BaseModel):
    name: str = Field(..., examples=["Администратор системы."])


class RoleUpdate(BaseModel):
    name_column: str = Field(..., examples=["name"])
    value: str = Field(..., examples=["Moderator"])


class SingleRoleResponse(BaseResponseBody):
    data: RoleBase | list


class SeveralRolesResponse(BaseResponseBody):
    data: list[RoleBase] | list
