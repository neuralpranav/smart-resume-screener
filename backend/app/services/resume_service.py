import os
import uuid
import re
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.candidate import Candidate, Resume
from app.schemas.candidate import ResumeSummary
from app.services.parser_service import (
    validate_file,
    extract_text_from_file,
    extract_candidate_info,
)
from app.core.exceptions import NotFoundException

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")


def ensure_upload_dir() -> str:
    """Ensure the local uploads directory exists."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    return UPLOAD_DIR


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal or invalid characters."""
    clean = re.sub(r"[^\w\-.]", "_", os.path.basename(filename))
    return clean or "resume"


def process_and_save_resume(db: Session, file_bytes: bytes, filename: str) -> Resume:
    """
    Validate, extract text and metadata, link/create Candidate, and persist Resume.
    """
    file_type = validate_file(file_bytes, filename)
    raw_text = extract_text_from_file(file_bytes, filename)
    extracted_info = extract_candidate_info(raw_text)

    # 1. Check or create candidate record
    candidate: Optional[Candidate] = None
    email = extracted_info.get("email")
    if email:
        candidate = db.query(Candidate).filter(Candidate.email == email).first()

    if not candidate:
        candidate = Candidate(
            full_name=extracted_info.get("full_name") or "Unknown Candidate",
            email=email,
            phone=extracted_info.get("phone"),
            location=extracted_info.get("location"),
        )
        db.add(candidate)
        db.flush()  # Generate candidate.id before linking
    else:
        # Update existing candidate contact info if new info was detected
        if extracted_info.get("phone") and not candidate.phone:
            candidate.phone = extracted_info["phone"]
        if extracted_info.get("location") and not candidate.location:
            candidate.location = extracted_info["location"]

    # 2. Persist physical file locally
    uploads_path = ensure_upload_dir()
    safe_name = sanitize_filename(filename)
    unique_filename = f"{uuid.uuid4()}_{safe_name}"
    full_file_path = os.path.join(uploads_path, unique_filename)

    try:
        with open(full_file_path, "wb") as f:
            f.write(file_bytes)
    except Exception:
        full_file_path = None

    # 3. Create and store Resume record
    resume = Resume(
        candidate_id=candidate.id,
        filename=filename,
        file_path=full_file_path,
        file_type=file_type,
        raw_text=raw_text,
        extracted_skills=extracted_info.get("skills", []),
        extracted_experience_years=extracted_info.get("experience_years"),
        extracted_education=extracted_info.get("education", []),
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


def get_resume(db: Session, resume_id: str) -> Resume:
    """Retrieve Resume record with associated Candidate, or raise NotFoundException."""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise NotFoundException(f"Resume with ID '{resume_id}' not found.")
    return resume


def list_resumes(db: Session, skip: int = 0, limit: int = 100) -> List[ResumeSummary]:
    """List all uploaded resumes with candidate summaries ordered by upload time descending."""
    resumes = (
        db.query(Resume)
        .order_by(Resume.uploaded_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    summaries = []
    for res in resumes:
        cand_name = res.candidate.full_name if res.candidate else "Unknown Candidate"
        summaries.append(
            ResumeSummary(
                id=res.id,
                filename=res.filename,
                file_type=res.file_type,
                candidate_name=cand_name,
                extracted_skills=res.extracted_skills,
                extracted_experience_years=res.extracted_experience_years,
                uploaded_at=res.uploaded_at,
            )
        )
    return summaries


def delete_resume(db: Session, resume_id: str) -> None:
    """Delete Resume record and remove local physical file if present."""
    resume = get_resume(db, resume_id)
    if resume.file_path and os.path.exists(resume.file_path):
        try:
            os.remove(resume.file_path)
        except OSError:
            pass
    db.delete(resume)
    db.commit()
