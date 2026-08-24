from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.job import JobRead
from app.schemas.candidate import ResumeRead


class ScreeningResultBase(BaseModel):
    match_score: float = Field(..., ge=0.0, le=100.0, description="Overall matching score (0-100)", example=85.5)
    fit_level: str = Field(..., description="Fit category: Strong Match, Moderate Match, or Low Match", example="Strong Match")
    matched_skills: List[str] = Field(default_factory=list, description="Skills present in both JD and resume")
    missing_skills: List[str] = Field(default_factory=list, description="Required/preferred skills missing from resume")
    strengths: List[str] = Field(default_factory=list, description="Key candidate strengths identified")
    weaknesses: List[str] = Field(default_factory=list, description="Identified candidate gaps")
    justification: str = Field(..., description="Explainable rationale behind the evaluation score")
    is_shortlisted: bool = Field(default=False, description="Whether the candidate is marked as shortlisted")


class ScreeningRequest(BaseModel):
    job_id: str = Field(..., description="Target Job Description ID")
    resume_id: str = Field(..., description="Resume ID to screen")


class BatchScreeningRequest(BaseModel):
    job_id: str = Field(..., description="Target Job Description ID")
    resume_ids: Optional[List[str]] = Field(None, description="Optional list of Resume IDs. If omitted or empty, all uploaded resumes will be screened.")


class ScreeningResultCreate(ScreeningResultBase):
    job_id: str
    resume_id: str


class ScreeningResultRead(ScreeningResultBase):
    id: str
    job_id: str
    resume_id: str
    screened_at: datetime
    resume: Optional[ResumeRead] = None
    job: Optional[JobRead] = None

    model_config = ConfigDict(from_attributes=True)


class ShortlistToggleRequest(BaseModel):
    is_shortlisted: bool = Field(..., description="New shortlisted status")


class RankedCandidate(BaseModel):
    screening_id: str
    resume_id: str
    candidate_name: str
    candidate_email: Optional[str] = None
    filename: str
    match_score: float
    fit_level: str
    matched_skills: List[str]
    missing_skills: List[str]
    strengths: List[str]
    weaknesses: List[str]
    justification: str
    is_shortlisted: bool
    screened_at: datetime

    model_config = ConfigDict(from_attributes=True)
