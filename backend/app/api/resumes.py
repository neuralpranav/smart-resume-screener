from typing import List
from fastapi import APIRouter, Depends, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.candidate import ResumeRead, ResumeSummary
from app.schemas.common import MessageResponse
from app.services import resume_service

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.post("/upload", response_model=ResumeRead, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(..., description="PDF or TXT resume file"),
    db: Session = Depends(get_db),
) -> ResumeRead:
    """
    Upload and parse a single resume file (PDF or TXT).
    Extracts text, candidate contact info, skills, and persists candidate & resume records.
    """
    file_bytes = await file.read()
    filename = file.filename or "resume.pdf"
    return resume_service.process_and_save_resume(db=db, file_bytes=file_bytes, filename=filename)


@router.post("/upload-batch", response_model=List[ResumeRead], status_code=status.HTTP_201_CREATED)
async def upload_resumes_batch(
    files: List[UploadFile] = File(..., description="List of PDF or TXT resume files"),
    db: Session = Depends(get_db),
) -> List[ResumeRead]:
    """
    Batch upload and parse multiple resume files.
    """
    uploaded_resumes: List[ResumeRead] = []
    for file in files:
        file_bytes = await file.read()
        filename = file.filename or "resume.pdf"
        res = resume_service.process_and_save_resume(db=db, file_bytes=file_bytes, filename=filename)
        uploaded_resumes.append(res)
    return uploaded_resumes


@router.get("", response_model=List[ResumeSummary], status_code=status.HTTP_200_OK)
def list_resumes(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=100, description="Limit of results to return"),
    db: Session = Depends(get_db),
) -> List[ResumeSummary]:
    """List all uploaded resumes with candidate summaries."""
    return resume_service.list_resumes(db=db, skip=skip, limit=limit)


@router.get("/{resume_id}", response_model=ResumeRead, status_code=status.HTTP_200_OK)
def get_resume_details(resume_id: str, db: Session = Depends(get_db)) -> ResumeRead:
    """Get full details of a specific resume including candidate info and extracted raw text."""
    return resume_service.get_resume(db=db, resume_id=resume_id)


@router.delete("/{resume_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
def delete_resume_record(resume_id: str, db: Session = Depends(get_db)) -> MessageResponse:
    """Delete a resume record and associated file."""
    resume_service.delete_resume(db=db, resume_id=resume_id)
    return MessageResponse(message=f"Resume with ID '{resume_id}' was successfully deleted.")
