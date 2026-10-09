from datetime import datetime
from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from ..base import Base


class Document(Base):
    """SQLAlchemy model for the Document table."""

    __tablename__ = "documents_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str] = mapped_column(String(100))
    file_type: Mapped[str] = mapped_column(String(100))
    version: Mapped[int] = mapped_column()
    # A stable ID that represents the logical document.
    # Example: "HR-LEAVE-POLICY"
    document_key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Only the latest version should normally be used for retrieval.
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    file_hash: Mapped[str] = mapped_column(String(64))
    content_hash: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
