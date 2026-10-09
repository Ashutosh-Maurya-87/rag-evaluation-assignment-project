from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import select
import os
import hashlib

from ..models.document_chunk import DocumentChunk
from ..services.chunking import create_chunks
from ..db.database import get_db
from ..models.document import Document
from ..services.extractors.extractor import extract_text
from ..services.content import generate_content_hash

router = APIRouter()


@router.post("/upload_document")
async def upload_document(
    document_key: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # -------------------- BASIC VALIDATION --------------------

    # Check that the user provided a document key.
    document_key = document_key.strip()

    if not document_key:
        raise HTTPException(
            status_code=400,
            detail="Document key cannot be empty.",
        )

    # Check that a filename was provided.
    if not file.filename or "." not in file.filename:
        raise HTTPException(
            status_code=400,
            detail="A valid filename is required.",
        )

    # Get the file extension.
    file_type = file.filename.rsplit(".", 1)[-1].lower()

    # Allow only the file formats supported by our extractors.
    if file_type not in ["pdf", "csv", "xlsx", "xls"]:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, CSV, and Excel files are allowed.",
        )

    # -------------------- READ FILE AND CHECK FILE HASH --------------------

    # Read the uploaded file.
    file_byte = await file.read()

    # Reject an empty file.
    if not file_byte:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    # Calculate a hash of the original file bytes.
    # This identifies an exact duplicate file.
    file_hash = hashlib.sha256(file_byte).hexdigest()

    # -------------------- VERSION CHECK LOGIC --------------------

    # Find all versions belonging to this logical document.
    existing_versions = db.scalars(
        select(Document)
        .where(Document.document_key == document_key)
        .order_by(Document.version.desc())
    ).all()

    # The first result is the latest version, if one exists.
    latest_version = existing_versions[0] if existing_versions else None

    # Reject the same exact file if it was already uploaded
    # for this document key.
    if latest_version and latest_version.file_hash == file_hash:
        raise HTTPException(
            status_code=400,
            detail="This exact file has already been uploaded.",
        )

    # -------------------- SAVE FILE AND EXTRACT CONTENT --------------------

    # Create the upload directory if it doesn't exist.
    upload_folder = "uploads"
    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, file.filename)

    # Save the file so the existing extractors can read it.
    with open(file_path, "wb") as buffer:
        buffer.write(file_byte)

    try:
        # Extract text from the PDF, CSV, or Excel file.
        text = extract_text(file_path, file_type)

        # Split the extracted text into searchable chunks.
        chunks = create_chunks(text)

        # Calculate a hash of normalized extracted text.
        # This helps detect content that hasn't actually changed.
        content_hash = generate_content_hash(text)

    except Exception as exc:
        # Don't return internal file-processing details to the client.
        raise HTTPException(
            status_code=422,
            detail="The uploaded file could not be processed.",
        ) from exc

    # Reject files that contain no usable text or chunks.
    if not text.strip() or not chunks:
        raise HTTPException(
            status_code=422,
            detail="No usable text was found in the uploaded file.",
        )

    # Reject unchanged content, even if the file bytes differ.
    if latest_version and latest_version.content_hash == content_hash:
        raise HTTPException(
            status_code=400,
            detail="The document content has not changed.",
        )

    # -------------------- CHECK CONTENT DUPLICATES --------------------

    # Don't allow identical extracted content under another document key.
    # If your business rules allow two policies to have identical content,
    # we can remove this global check later.
    existing_content_document = db.scalars(
        select(Document).where(Document.content_hash == content_hash)
    ).first()

    if existing_content_document:
        raise HTTPException(
            status_code=400,
            detail=(
                "The same extracted content already exists. "
                f"Document ID: {existing_content_document.id}"
            ),
        )

    # -------------------- CALCULATE NEW VERSION --------------------

    # A new logical document starts at version 1.
    # An updated document gets the previous version number plus 1.
    new_version = (
        latest_version.version + 1
        if latest_version
        else 1
    )

    # -------------------- DOCUMENT CREATION LOGIC --------------------

    try:
        # Deactivate the previous version, if this is an update.
        if latest_version:
            latest_version.is_active = False

        # Create the new document version.
        document = Document(
            document_key=document_key,
            file_name=file.filename,
            file_type=file_type,
            version=new_version,
            is_active=True,
            file_hash=file_hash,
            content_hash=content_hash,
            status="completed",
        )

        # Add the new document to the current database transaction.
        db.add(document)

        # Flush inserts the document so we can use its generated ID.
        # It does not commit the transaction yet.
        db.flush()

        # -------------------- CHUNK CREATION LOGIC --------------------

        # Save every chunk and associate it with this document version.
        for index, chunk_text in enumerate(chunks):
            chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                content=chunk_text,
            )

            db.add(chunk)

        # -------------------- COMMIT DATABASE CHANGES --------------------

        # Save the new version, its chunks, and the previous version's
        # inactive status together in one transaction.
        db.commit()

        # Refresh the object to read its saved database values.
        db.refresh(document)

    except Exception:
        # Undo database changes if any database operation fails.
        db.rollback()
        raise

    # -------------------- SUCCESS RESPONSE --------------------

    return {
        "message": "Document version uploaded successfully.",
        "document_id": document.id,
        "document_key": document.document_key,
        "version": document.version,
        "is_active": document.is_active,
        "file_name": document.file_name,
        "file_type": document.file_type,
        "chunks_created": len(chunks),
    }
