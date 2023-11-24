from typing import List

from sqlalchemy import Table, Column, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base, TimeStampedMixin

"""Модель ассоциативной таблица для связи MtM м/у ролями и пользователями."""
roles_to_users = Table(
    "roles_to_users",
    Base.metadata,
    Column(
        "user_id", ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True
    ),
    Column(
        "role_id", ForeignKey("roles.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True
    ),
)


class Role(Base, TimeStampedMixin):
    """Модель таблицы с ролями."""

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    users: Mapped[List["User"]] = relationship(secondary=roles_to_users, back_populates="roles")

    def __repr__(self) -> str:
        return f"Role(id={self.id!r}, name={self.name!r})"
