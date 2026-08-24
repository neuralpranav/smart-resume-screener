from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.screening import (
    ScreeningRequest,
    BatchScreeningRequest,
    ScreeningResultRead,
    ShortlistToggleRequest,
    RankedCandidate,
)
from app.services import screening_service

router = APIRouter(prefix="/screen", tags=["Screening"])


@router.post("", response_model=ScreeningResultRead, status_code=status.HTTP_200_OK)
def screen_single_resume(
    request: ScreeningRequest, db: Session = Depends(get_db)
) -> ScreeningResultRead:
    """
    Screen a single candidate resume against a job description.
    Computes semantic/rubric match score, matched/missing skills, strengths, weaknesses, and stores the result.
    """
    return screening_service.screen_resume(
        db=db, job_id=request.job_id, resume_id=request.resume_id
    )


@router.post("/batch", response_model=List[ScreeningResultRead], status_code=status.HTTP_200_OK)
def screen_multiple_resumes(
    request: BatchScreeningRequest, db: Session = Depends(get_db)
) -> List[ScreeningResultRead]:
    """
    Screen a list of resumes (or all resumes if none specified) against a job description.
    """
    return screening_service.batch_screen(
        db=db, job_id=request.job_id, resume_ids=request.resume_ids
    )


@router.get("/{screening_id}", response_model=ScreeningResultRead, status_code=status.HTTP_200_OK)
def get_screening_details(screening_id: str, db: Session = Depends(get_db)) -> ScreeningResultRead:
    """Get full details and explainability breakdown of a specific screening evaluation."""
    return screening_service.get_screening_result(db=db, screening_id=screening_id)


@router.get("/job/{job_id}/results", response_model=List[ScreeningResultRead], status_code=status.HTTP_200_OK)
def get_job_screening_results(job_id: str, db: Session = Depends(get_db)) -> List[ScreeningResultRead]:
    """Get all screening results associated with a specific job description."""
    return screening_service.get_job_screening_results(db=db, job_id=job_id)


@router.get("/job/{job_id}/rankings", response_model=List[RankedCandidate], status_code=status.HTTP_200_OK)
def get_job_ranked_candidates(
    job_id: str,
    min_score: Optional[float] = Query(None, ge=0.0, le=100.0, description="Filter candidates by minimum match score"),
    shortlisted_only: bool = Query(False, description="Filter to only show shortlisted candidates"),
    db: Session = Depends(get_db),
) -> List[RankedCandidate]:
    """
    Return candidate leaderboard for a job ranked by match score descending.
    Allows filtering by minimum score and shortlist status.
    """
    return screening_service.get_ranked_candidates(
        db=db, job_id=job_id, min_score=min_score, shortlisted_only=shortlisted_only
    )


@router.patch("/{screening_id}/shortlist", response_model=ScreeningResultRead, status_code=status.HTTP_200_OK)
def toggle_candidate_shortlist(
    screening_id: str,
    request: ShortlistToggleRequest,
    db: Session = Depends(get_db),
) -> ScreeningResultRead:
    """Manually update or toggle candidate shortlisted status."""
    return screening_service.toggle_shortlist(
        db=db, screening_id=screening_id, is_shortlisted=request.is_shortlisted
    )
