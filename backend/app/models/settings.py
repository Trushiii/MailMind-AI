from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.database.session import Base

class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    telegram_chat_id: Mapped[str] = mapped_column(String(50), nullable=True)