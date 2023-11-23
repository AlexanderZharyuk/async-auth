from pydantic import BaseModel, Field

from src.schemas import BaseResponseBody


class RoleUser(BaseModel):
    role_id: int = Field(..., examples=["127856"])


class SingleUserResponse(BaseResponseBody):
    data: dict
