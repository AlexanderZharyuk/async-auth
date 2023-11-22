from sqlalchemy import UUID, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base, TimeStampedMixin
from src.v1.users.models import User


class UsersSignatures(Base, TimeStampedMixin):
    __tablename__ = "users_signatures"

    signature: Mapped[str] = mapped_column(String(120), primary_key=True, unique=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), unique=True)
    user: Mapped[User] = relationship("User", back_populates="signature")

    def __repr__(self) -> str:
        return f"UserSignature(User: {self.user}, Token: {self.token})"
