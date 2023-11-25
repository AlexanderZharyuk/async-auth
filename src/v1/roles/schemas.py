from typing import Optional

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
    name: Optional[str] = Field(..., examples=["Модератор системы."])


class SingleRoleResponse(BaseResponseBody):
    data: RoleBase | dict


class SeveralRolesResponse(BaseResponseBody):
    data: list[RoleBase] | dict
