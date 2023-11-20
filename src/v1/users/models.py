import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, UUID, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base, TimeStampedMixin


class User(Base, TimeStampedMixin):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(512), default=None, nullable=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(), nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean(), default=False, nullable=False)
    last_login: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )

    # ToDo: Relationships: MtM table for roles (echeck cascade)
    # roles: Mapped[List[RolesToUsers]] = relationship(back_populates="users")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, login={self.username!r}, name={self.full_name!r}, email={self.email!r})"
