from datetime import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base

class EmailAccount(Base):
    __tablename__ = "email_accounts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    provider: Mapped[str] = mapped_column(String(50), default="gmail")
    email_address: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    
    # Store encrypted tokens
    encrypted_access_token: Mapped[str] = mapped_column(String, nullable=True)
    encrypted_refresh_token: Mapped[str] = mapped_column(String, nullable=True)
    token_expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationship to emails
    emails: Mapped[list["EmailMessage"]] = relationship(back_populates="account", cascade="all, delete-orphan")