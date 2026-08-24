from typing import List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.job import JobCreate, JobUpdate, JobRead
from app.schemas.common import MessageResponse
from app.services import job_service

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("", response_model=JobRead, status_code=status.HTTP_201_CREATED)
def create_job_posting(job_in: JobCreate, db: Session = Depends(get_db)) -> JobRead:
    """Create a new job description posting."""
    return job_service.create_job(db=db, job_in=job_in)


@router.get("", response_model=List[JobRead], status_code=status.HTTP_200_OK)
def list_job_postings(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=100, description="Limit of results to return"),
    db: Session = Depends(get_db),
) -> List[JobRead]:
    """List all job descriptions ordered by creation time descending."""
    return job_service.list_jobs(db=db, skip=skip, limit=limit)


@router.get("/{job_id}", response_model=JobRead, status_code=status.HTTP_200_OK)
def get_job_posting(job_id: str, db: Session = Depends(get_db)) -> JobRead:
    """Get details of a specific job description by ID."""
    return job_service.get_job(db=db, job_id=job_id)


@router.put("/{job_id}", response_model=JobRead, status_code=status.HTTP_200_OK)
def update_job_posting(
    job_id: str, job_update: JobUpdate, db: Session = Depends(get_db)
) -> JobRead:
    """Update fields of an existing job description."""
    return job_service.update_job(db=db, job_id=job_id, job_update=job_update)


@router.delete("/{job_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
def delete_job_posting(job_id: str, db: Session = Depends(get_db)) -> MessageResponse:
    """Delete a job description and its associated screening results."""
    job_service.delete_job(db=db, job_id=job_id)
    return MessageResponse(message=f"Job Description with ID '{job_id}' was successfully deleted.")
