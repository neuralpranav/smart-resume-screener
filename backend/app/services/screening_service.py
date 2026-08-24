from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.screening import ScreeningResult
from app.models.candidate import Resume
from app.schemas.screening import RankedCandidate
from app.services.job_service import get_job
from app.services.resume_service import get_resume
from app.services.evaluation_service import evaluate_candidate_resume
from app.core.exceptions import NotFoundException


def screen_resume(db: Session, job_id: str, resume_id: str) -> ScreeningResult:
    """
    Evaluate a candidate's resume against a job description,
    save the screening evaluation, and return the ScreeningResult.
    """
    job = get_job(db, job_id)
    resume = get_resume(db, resume_id)

    cand_name = resume.candidate.full_name if resume.candidate else "Unknown Candidate"
    
    # Perform explainable evaluation
    eval_result = evaluate_candidate_resume(
        job=job,
        candidate_name=cand_name,
        resume_raw_text=resume.raw_text,
        extracted_skills=resume.extracted_skills,
        extracted_experience_years=resume.extracted_experience_years,
        extracted_education=resume.extracted_education,
    )

    # Check if a screening result already exists for this job & resume
    screening = (
        db.query(ScreeningResult)
        .filter(ScreeningResult.job_id == job_id, ScreeningResult.resume_id == resume_id)
        .first()
    )

    if screening:
        # Update existing record
        screening.match_score = eval_result["match_score"]
        screening.fit_level = eval_result["fit_level"]
        screening.matched_skills = eval_result["matched_skills"]
        screening.missing_skills = eval_result["missing_skills"]
        screening.strengths = eval_result["strengths"]
        screening.weaknesses = eval_result["weaknesses"]
        screening.justification = eval_result["justification"]
        screening.is_shortlisted = eval_result["is_shortlisted"]
        screening.screened_at = datetime.now(timezone.utc)
    else:
        # Create new record
        screening = ScreeningResult(
            job_id=job_id,
            resume_id=resume_id,
            match_score=eval_result["match_score"],
            fit_level=eval_result["fit_level"],
            matched_skills=eval_result["matched_skills"],
            missing_skills=eval_result["missing_skills"],
            strengths=eval_result["strengths"],
            weaknesses=eval_result["weaknesses"],
            justification=eval_result["justification"],
            is_shortlisted=eval_result["is_shortlisted"],
            screened_at=datetime.now(timezone.utc),
        )
        db.add(screening)

    db.commit()
    db.refresh(screening)
    return screening


def batch_screen(
    db: Session, job_id: str, resume_ids: Optional[List[str]] = None
) -> List[ScreeningResult]:
    """
    Screen multiple resumes (or all available resumes) against a job description.
    """
    get_job(db, job_id)  # Validate job exists

    if not resume_ids:
        # Retrieve all available resumes
        all_resumes = db.query(Resume.id).all()
        target_ids = [r[0] for r in all_resumes]
    else:
        target_ids = resume_ids

    results: List[ScreeningResult] = []
    for res_id in target_ids:
        res = screen_resume(db, job_id, res_id)
        results.append(res)

    return results


def get_screening_result(db: Session, screening_id: str) -> ScreeningResult:
    """Retrieve a screening result by ID or raise NotFoundException."""
    screening = db.query(ScreeningResult).filter(ScreeningResult.id == screening_id).first()
    if not screening:
        raise NotFoundException(f"Screening result with ID '{screening_id}' not found.")
    return screening


def get_job_screening_results(db: Session, job_id: str) -> List[ScreeningResult]:
    """Retrieve all screening results for a job ordered by score descending."""
    get_job(db, job_id)  # Validate job exists
    return (
        db.query(ScreeningResult)
        .filter(ScreeningResult.job_id == job_id)
        .order_by(ScreeningResult.match_score.desc())
        .all()
    )


def get_ranked_candidates(
    db: Session,
    job_id: str,
    min_score: Optional[float] = None,
    shortlisted_only: bool = False,
) -> List[RankedCandidate]:
    """
    Return candidates ranked by match_score descending with optional filtering.
    """
    get_job(db, job_id)  # Validate job exists

    query = db.query(ScreeningResult).filter(ScreeningResult.job_id == job_id)

    if min_score is not None:
        query = query.filter(ScreeningResult.match_score >= min_score)

    if shortlisted_only:
        query = query.filter(ScreeningResult.is_shortlisted.is_(True))

    results = query.order_by(ScreeningResult.match_score.desc()).all()

    ranked: List[RankedCandidate] = []
    for s in results:
        resume = s.resume
        cand_name = (
            resume.candidate.full_name if (resume and resume.candidate) else "Unknown Candidate"
        )
        cand_email = (
            resume.candidate.email if (resume and resume.candidate) else None
        )
        filename = resume.filename if resume else "resume"

        ranked.append(
            RankedCandidate(
                screening_id=s.id,
                resume_id=s.resume_id,
                candidate_name=cand_name,
                candidate_email=cand_email,
                filename=filename,
                match_score=s.match_score,
                fit_level=s.fit_level,
                matched_skills=s.matched_skills,
                missing_skills=s.missing_skills,
                strengths=s.strengths,
                weaknesses=s.weaknesses,
                justification=s.justification,
                is_shortlisted=s.is_shortlisted,
                screened_at=s.screened_at,
            )
        )

    return ranked


def toggle_shortlist(db: Session, screening_id: str, is_shortlisted: bool) -> ScreeningResult:
    """Update the shortlisted status of a candidate screening result."""
    screening = get_screening_result(db, screening_id)
    screening.is_shortlisted = is_shortlisted
    db.commit()
    db.refresh(screening)
    return screening
