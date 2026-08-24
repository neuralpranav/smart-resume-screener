from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.job import JobDescription
from app.schemas.job import JobCreate, JobUpdate
from app.core.exceptions import NotFoundException


def create_job(db: Session, job_in: JobCreate) -> JobDescription:
    """Create and persist a new Job Description."""
    job = JobDescription(
        title=job_in.title,
        department=job_in.department,
        description=job_in.description,
        required_skills=job_in.required_skills,
        preferred_skills=job_in.preferred_skills,
        min_experience_years=job_in.min_experience_years,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_job(db: Session, job_id: str) -> JobDescription:
    """Retrieve a Job Description by ID or raise NotFoundException."""
    job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    if not job:
        raise NotFoundException(f"Job Description with ID '{job_id}' not found.")
    return job


def list_jobs(db: Session, skip: int = 0, limit: int = 100) -> List[JobDescription]:
    """List all Job Descriptions ordered by creation time descending."""
    return (
        db.query(JobDescription)
        .order_by(JobDescription.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_job(db: Session, job_id: str, job_update: JobUpdate) -> JobDescription:
    """Update fields of an existing Job Description."""
    job = get_job(db, job_id)
    update_data = job_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)
    
    db.commit()
    db.refresh(job)
    return job


def delete_job(db: Session, job_id: str) -> None:
    """Delete a Job Description by ID."""
    job = get_job(db, job_id)
    db.delete(job)
    db.commit()
