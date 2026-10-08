from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import select
import os
import hashlib
from ..db.database import get_db
from ..models.document import Document
from ..services.extractors.extractor import extract_text
from ..services.content import generate_content_hash

router = APIRouter()


@router.post("/upload_document")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    upload_folder = "uploads"
    # make sure the upload folder exists.
    os.makedirs(upload_folder, exist_ok=True)

    # split the file name to get the file type.
    file_type = file.filename.split(".")[-1].lower()

    if file_type not in ["pdf", "csv", "xlsx", "xls"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Only PDF, CSV, and Excel files are allowed.",
        )
    # read the file bytes.
    file_byte = await file.read()

    # calculate the hash of the file content.
    file_hash = hashlib.sha256(file_byte).hexdigest()

    existing_document = db.scalars(
        select(Document).where(Document.file_hash == file_hash)
    ).first()

    if existing_document:
        raise HTTPException(
            status_code=400,
            detail=f"A document with the same content already exists. ID: {existing_document.id}",
        )

    #  save the file to the upload folder.
    file_path = os.path.join(upload_folder, file.filename)

    # write the file bytes to the file path.
    with open(file_path, "wb") as buffer:
        buffer.write(file_byte)

    text = extract_text(file_path, file_type)
    content_hash = generate_content_hash(text)
    
    existing_content_document = db.scalars(
        select(Document).where(Document.content_hash == content_hash)
    ).first()

    if existing_content_document:
        raise HTTPException(
            status_code=400,
            detail=f"A document with the same content already exists. ID: {existing_content_document.id}",
        )
    document = Document(
        file_name=file.filename,
        file_type=file_type,
        version=1,
        file_hash=file_hash,
        content_hash=content_hash,
        status="completed",
    )

    db.add(document)
    db.commit()
    db.refresh(document)
    print("FILE:", file.filename)
    print("TYPE:", file_type)
    print("TEXT:")
    print(text)
    print("HASH:", file_hash)
    print("CONTENT HASH:", content_hash)

    return {
        "message": "File uploaded and extracted successfully",
        "file_name": file.filename,
        "file_type": file_type,
    }
