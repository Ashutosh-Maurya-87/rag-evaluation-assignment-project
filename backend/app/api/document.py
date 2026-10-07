from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..db.database import get_db
from ..models.document import Document

router = APIRouter()


@router.post("/upload_document")
def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    print(file.filename)
    print(file.content_type)

    return {"message": "File received successfully"}
