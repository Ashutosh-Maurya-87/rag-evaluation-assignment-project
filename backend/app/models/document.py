from datetime import datetime

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from ..base import Base


class Document(Base):
    """SQLAlchemy model for the Document table."""

    __tablename__ = "documents_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str] = mapped_column(String(100))
    file_type: Mapped[str] = mapped_column(String(100))
    version: Mapped[int] = mapped_column()
    file_hash: Mapped[str] = mapped_column(String(64)) 
    content_hash: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
