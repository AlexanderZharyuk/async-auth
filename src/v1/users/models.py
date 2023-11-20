import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import UUID, Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(512), nullable=False, default="")
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(), nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean(), default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True, default=None
    )
    last_login: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )

    roles: Mapped[List["RolesToUsers"]] = relationship(back_populates="users")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, login={self.username!r}, name={self.full_name!r}, email={self.email!r})"
