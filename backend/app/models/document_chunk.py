from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class DocumentChunk(Base):
    # This table stores the smaller pieces created from each document.
    __tablename__ = "document_chunks"

    # Unique ID for every chunk.
    id: Mapped[int] = mapped_column(primary_key=True)

    # This tells us which document this chunk belongs to.
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents_table.id"),
        nullable=False,
    )

    # This tells us the order of the chunk inside the document.
    # Example: 0 = first chunk, 1 = second chunk, etc.
    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # The actual text that we will later send for embedding.
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # For PDFs, we can keep track of which page this chunk came from.
    # It can be NULL for CSV/Excel files.
    page_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # Later this helps us show where an answer came from.
    # Example: "Annual Leave" or "Remote Work".
    section: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # When this chunk was created.
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
    )
