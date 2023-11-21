from datetime import datetime
from typing import List

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base, TimeStampedMixin


class Role(Base, TimeStampedMixin):
    """Модель таблицы с ролями."""

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    def __repr__(self) -> str:
        return f"Role(id={self.id!r}, name={self.name!r})"


class RolesToUsers(Base):
    """Модель ассоциативной таблица для связи MtM м/у ролями и пользователями."""

    __tablename__ = "roles_to_users"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), primary_key=True)
