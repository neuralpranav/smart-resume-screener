import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class ScreeningResult(Base):
    __tablename__ = "screening_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id = Column(String(36), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Evaluation Scores & Output
    match_score = Column(Float, nullable=False, default=0.0)  # 0 to 100
    fit_level = Column(String(50), nullable=False)           # 'Strong Match', 'Moderate Match', 'Low Match'
    matched_skills = Column(JSON, default=list, nullable=False)
    missing_skills = Column(JSON, default=list, nullable=False)
    strengths = Column(JSON, default=list, nullable=False)
    weaknesses = Column(JSON, default=list, nullable=False)
    justification = Column(Text, nullable=False)
    is_shortlisted = Column(Boolean, default=False, nullable=False, index=True)
    screened_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    job = relationship("JobDescription", back_populates="screening_results")
    resume = relationship("Resume", back_populates="screening_results")
