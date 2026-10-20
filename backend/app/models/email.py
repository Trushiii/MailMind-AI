from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base

class EmailMessage(Base):
    __tablename__ = "email_messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("email_accounts.id"))
    provider_message_id: Mapped[str] = mapped_column(String, index=True)
    
    thread_id: Mapped[str] = mapped_column(String, index=True, nullable=True)
    sender: Mapped[str] = mapped_column(String, nullable=True)
    subject: Mapped[str] = mapped_column(String, nullable=True)
    snippet: Mapped[str] = mapped_column(Text, nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    # These are the fields that were missing
    ai_summary: Mapped[str] = mapped_column(Text, nullable=True)
    ai_category: Mapped[str] = mapped_column(String(100), nullable=True)
    ai_priority: Mapped[str] = mapped_column(String(50), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    account: Mapped["EmailAccount"] = relationship(back_populates="emails")
    tasks: Mapped[list["Task"]] = relationship(back_populates="email", cascade="all, delete-orphan")

    # Ensure no duplicate emails from the same provider
    __table_args__ = (
        UniqueConstraint('account_id', 'provider_message_id', name='uq_account_message'),
    )