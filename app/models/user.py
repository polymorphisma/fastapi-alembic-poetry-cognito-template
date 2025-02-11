from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, intpk


class User(Base):
    __tablename__ = "user"

    id: Mapped[intpk]
    username: Mapped[str]
    sub: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name: Mapped[str]
    email: Mapped[str]
    email_verified: Mapped[bool] = mapped_column(default=False)
    salt: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=True)

    # Define the relationship to the other models
    connectors = relationship("Connector", back_populates="user")
    projects = relationship("Project", back_populates="user")


class TempUser(Base):
    __tablename__ = "temp_user_data"

    id: Mapped[intpk]
    username: Mapped[str]
    password: Mapped[str]
    name: Mapped[str | None]
    email: Mapped[str]
