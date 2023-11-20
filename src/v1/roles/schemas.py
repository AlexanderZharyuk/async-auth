from datetime import datetime
from pydantic import BaseModel, Field

from src.models import BaseResponseBody


class Role(BaseModel):
    id: int | None = Field(..., examples=["127856"])
    name: str = Field(
        ..., examples=["Администратор системы."]
    )
    created_at: datetime | None = Field(..., examples=[datetime.now()])

    class Config:
        populate_by_name = True


class SeveralRolesResponse(BaseResponseBody):
    data: list[Role]