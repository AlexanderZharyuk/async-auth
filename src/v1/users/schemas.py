from pydantic import BaseModel, Field

class RoleUser(BaseModel):
    role_id: int = Field(..., examples=["127856"])