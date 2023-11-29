import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import UUID, Boolean, DateTime, ForeignKey, String, select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Base, TimeStampedMixin
from src.v1.roles.models import Role, roles_to_users
from src.v1.roles.constants import RolesChoices


class User(Base, TimeStampedMixin):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(512), default=None, nullable=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    password: Mapped[str] = mapped_column(String(), nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean(), default=False, nullable=False)
    last_login: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )
    signature: Mapped["UserSignature"] = relationship(
        "UserSignature", uselist=False, back_populates="user", lazy="selectin"
    )
    logins: Mapped["UserLogin"] = relationship("UserLogin", back_populates="user", lazy="selectin")
    refresh_tokens: Mapped["UserRefreshTokens"] = relationship(
        "UserRefreshTokens", back_populates="user"
    )    
    roles: Mapped[List["Role"]] = relationship(
        secondary=roles_to_users, back_populates="users", lazy="selectin"
    )

    async def set_default_role(self, session: AsyncSession):
        statement = select(Role).where(Role.name == RolesChoices.DEFAULT)
        result = await session.execute(statement)
        default_role = result.scalar()
        self.roles = [default_role] 
        
    def __repr__(self) -> str:
        return f"User(id={self.id!r}, login={self.username!r}, full_name={self.full_name!r}, email={self.email!r})"


class UserSignature(Base, TimeStampedMixin):
    __tablename__ = "users_signatures"

    signature: Mapped[str] = mapped_column(String(120), primary_key=True, unique=True)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id",  ondelete="CASCADE", onupdate="CASCADE"),
        unique=True
    )
    user: Mapped[User] = relationship("User", back_populates="signature")

    def __repr__(self) -> str:
        return f"UserSignature(User: {self.user}, Signature: {self.signature})"


class UserLogin(Base, TimeStampedMixin):
    __tablename__ = "users_logins"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id",  ondelete="CASCADE", onupdate="CASCADE")
    )
    user: Mapped[User] = relationship("User", back_populates="logins")
    ip: Mapped[str] = mapped_column(String(120), nullable=False)
    user_agent: Mapped[str] = mapped_column(String(150), nullable=False)

    def __repr__(self) -> str:
        return f"UserLogin(User: {self.user}, IP: {self.ip}, Time: {self.updated_at})"


class UserRefreshTokens(Base, TimeStampedMixin):
    __tablename__ = "users_refresh_tokens"

    token: Mapped[str] = mapped_column(String(120), nullable=False, index=True, primary_key=True)
    expire_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id",  ondelete="CASCADE", onupdate="CASCADE")
    )
    user: Mapped[User] = relationship("User", back_populates="refresh_tokens")
