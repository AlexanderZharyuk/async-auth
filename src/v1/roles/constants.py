from pydantic import BaseModel


class Roles(BaseModel):
    DEFAULT: str = "default_user"
    GUEST: str = "guest"
    ADMIN: str = "admin"
    SUBSCRIBER: str = "subscriber"


RolesChoices = Roles()