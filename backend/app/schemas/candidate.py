from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, ConfigDict, Field


class CandidateBase(BaseModel):
    full_name: str = Field(..., description="Candidate's full name", example="Alex Johnson")
    email: Optional[str] = Field(None, description="Email address", example="alex.johnson@example.com")
    phone: Optional[str] = Field(None, description="Contact phone number", example="+1-555-0199")
    location: Optional[str] = Field(None, description="City / Country", example="San Francisco, CA")


class CandidateCreate(CandidateBase):
    pass


class CandidateRead(CandidateBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeBase(BaseModel):
    filename: str
    file_type: str
    raw_text: str
    extracted_skills: List[str] = Field(default_factory=list)
    extracted_experience_years: Optional[float] = None
    extracted_education: List[Any] = Field(default_factory=list)


class ResumeRead(ResumeBase):
    id: str
    candidate_id: Optional[str] = None
    candidate: Optional[CandidateRead] = None
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeSummary(BaseModel):
    id: str
    filename: str
    file_type: str
    candidate_name: Optional[str] = None
    extracted_skills: List[str] = Field(default_factory=list)
    extracted_experience_years: Optional[float] = None
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)
