from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class JobBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255, description="Job title", example="Senior Python Developer")
    department: Optional[str] = Field(None, max_length=100, description="Department or team name", example="Engineering")
    description: str = Field(..., min_length=10, description="Detailed job description")
    required_skills: List[str] = Field(default_factory=list, description="Must-have technical or domain skills", example=["Python", "FastAPI", "SQL"])
    preferred_skills: List[str] = Field(default_factory=list, description="Nice-to-have skills", example=["Docker", "AWS"])
    min_experience_years: int = Field(default=0, ge=0, description="Minimum required years of experience", example=3)


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    department: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, min_length=10)
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    min_experience_years: Optional[int] = Field(None, ge=0)


class JobRead(JobBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
