import re
from typing import Dict, List, Optional, Any, Protocol
from app.models.job import JobDescription
from app.schemas.job import JobRead


def _normalize_skill(skill: str) -> str:
    """Normalize skill string for resilient comparison."""
    return re.sub(r"[^\w\s]", "", skill).strip().lower()


def _is_skill_present(skill: str, candidate_skills: List[str], raw_text: str) -> bool:
    """
    Check if a skill is present in candidate's extracted skills list
    or directly mentioned in the resume text using word boundary matching.
    """
    norm_skill = _normalize_skill(skill)
    cand_norm = [_normalize_skill(s) for s in candidate_skills]
    
    # Direct list match
    if norm_skill in cand_norm:
        return True
    
    # Text search with word boundary (handles special chars like c++, c#, .net)
    escaped_skill = re.escape(skill.strip())
    pattern = rf"(?:\b|_){escaped_skill}(?:\b|_)"
    if re.search(pattern, raw_text, re.IGNORECASE):
        return True
        
    return False


class BaseEvaluator(Protocol):
    """Protocol interface for resume evaluation engines (rule-based or LLM)."""
    def evaluate(
        self,
        job_title: str,
        job_description: str,
        required_skills: List[str],
        preferred_skills: List[str],
        min_experience_years: int,
        candidate_name: str,
        resume_raw_text: str,
        extracted_skills: List[str],
        extracted_experience_years: Optional[float],
        extracted_education: List[Any],
    ) -> Dict[str, Any]:
        ...


class RuleBasedEvaluator:
    """
    Deterministic, offline-first evaluation engine.
    Calculates explainable scores and detailed justifications based on weighted rubrics:
    - Required Skills Coverage: 45%
    - Preferred Skills Coverage: 20%
    - Experience Alignment:     20%
    - Education & Domain Fit:   15%
    """

    def evaluate(
        self,
        job_title: str,
        job_description: str,
        required_skills: List[str],
        preferred_skills: List[str],
        min_experience_years: int,
        candidate_name: str,
        resume_raw_text: str,
        extracted_skills: List[str],
        extracted_experience_years: Optional[float],
        extracted_education: List[Any],
    ) -> Dict[str, Any]:
        
        # 1. Required Skills Evaluation (45 pts max)
        matched_required: List[str] = []
        missing_required: List[str] = []

        for req in required_skills:
            if _is_skill_present(req, extracted_skills, resume_raw_text):
                matched_required.append(req)
            else:
                missing_required.append(req)

        if required_skills:
            req_score = (len(matched_required) / len(required_skills)) * 45.0
        else:
            # If no required skills specified, full points
            req_score = 45.0

        # 2. Preferred Skills Evaluation (20 pts max)
        matched_preferred: List[str] = []
        missing_preferred: List[str] = []

        for pref in preferred_skills:
            if _is_skill_present(pref, extracted_skills, resume_raw_text):
                matched_preferred.append(pref)
            else:
                missing_preferred.append(pref)

        if preferred_skills:
            pref_score = (len(matched_preferred) / len(preferred_skills)) * 20.0
        else:
            pref_score = 20.0

        # 3. Experience Evaluation (20 pts max)
        exp_score = 0.0
        exp_feedback = ""
        cand_exp = extracted_experience_years

        if min_experience_years <= 0:
            exp_score = 20.0
            exp_feedback = "No minimum experience requirement specified."
        elif cand_exp is not None:
            if cand_exp >= min_experience_years:
                exp_score = 20.0
                exp_feedback = f"Meets/exceeds experience requirement ({cand_exp} yrs vs {min_experience_years} yrs required)."
            else:
                ratio = max(0.0, cand_exp / min_experience_years)
                exp_score = round(ratio * 20.0, 1)
                exp_feedback = f"Candidate has approximately {cand_exp} yrs vs {min_experience_years} yrs target."
        else:
            # Not explicitly found; assign baseline 10/20 points
            exp_score = 10.0
            exp_feedback = "Experience duration could not be deterministically determined from resume text."

        # 4. Education & Domain Evaluation (15 pts max)
        edu_score = 10.0  # Baseline credit
        has_relevant_degree = False
        if extracted_education:
            edu_score = 15.0
            has_relevant_degree = True

        # Total Composite Score (0 - 100)
        total_score = round(req_score + pref_score + exp_score + edu_score, 1)
        total_score = min(100.0, max(0.0, total_score))

        # Determine Fit Level
        if total_score >= 75.0:
            fit_level = "Strong Match"
        elif total_score >= 50.0:
            fit_level = "Moderate Match"
        else:
            fit_level = "Low Match"

        # Combine matched & missing skills
        all_matched = list(dict.fromkeys(matched_required + matched_preferred))
        all_missing = list(dict.fromkeys(missing_required + missing_preferred))

        # Generate Explainable Strengths
        strengths: List[str] = []
        if matched_required:
            strengths.append(
                f"Matches {len(matched_required)}/{len(required_skills)} required skills: {', '.join(matched_required)}."
            )
        if matched_preferred:
            strengths.append(f"Possesses preferred skill(s): {', '.join(matched_preferred)}.")
        if cand_exp is not None and min_experience_years > 0 and cand_exp >= min_experience_years:
            strengths.append(f"Demonstrated experience level ({cand_exp} years) satisfies job requirements.")
        if has_relevant_degree:
            edu_preview = extracted_education[0] if len(extracted_education) > 0 else "Degree"
            strengths.append(f"Educational background present: {edu_preview}.")

        if not strengths:
            strengths.append("Candidate resume received and processed.")

        # Generate Explainable Weaknesses / Gaps
        weaknesses: List[str] = []
        if missing_required:
            weaknesses.append(f"Missing required core skill(s): {', '.join(missing_required)}.")
        if cand_exp is not None and min_experience_years > 0 and cand_exp < min_experience_years:
            weaknesses.append(
                f"Experience ({cand_exp} yrs) falls below the target requirement of {min_experience_years} yrs."
            )
        if missing_preferred:
            weaknesses.append(f"Missing preferred skill(s): {', '.join(missing_preferred)}.")

        # Construct Clear Justification
        justification_parts = [
            f"{candidate_name} is evaluated as a {fit_level} for the {job_title} role with an overall score of {total_score}/100.",
        ]
        if required_skills:
            justification_parts.append(
                f"Candidate covers {len(matched_required)} of {len(required_skills)} mandatory skills."
            )
        if exp_feedback:
            justification_parts.append(exp_feedback)
        if missing_required:
            justification_parts.append(f"Key areas for follow-up include: {', '.join(missing_required)}.")

        justification = " ".join(justification_parts)

        # Shortlist recommendation: Strong match or >= 70 score with minimal missing required skills
        is_shortlisted = total_score >= 70.0 and len(missing_required) <= (1 if len(required_skills) > 2 else 0)

        return {
            "match_score": total_score,
            "fit_level": fit_level,
            "matched_skills": all_matched,
            "missing_skills": all_missing,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "justification": justification,
            "is_shortlisted": is_shortlisted,
        }


# Default active evaluator is the rule-based evaluator
_default_evaluator: BaseEvaluator = RuleBasedEvaluator()


def evaluate_candidate_resume(
    job: JobDescription | JobRead | Dict[str, Any],
    candidate_name: str,
    resume_raw_text: str,
    extracted_skills: List[str],
    extracted_experience_years: Optional[float] = None,
    extracted_education: Optional[List[Any]] = None,
    evaluator: Optional[BaseEvaluator] = None,
) -> Dict[str, Any]:
    """
    Main evaluation entry point. Evaluates candidate resume information
    against a job description and returns structured evaluation metrics.
    """
    active_evaluator = evaluator or _default_evaluator

    # Extract fields from ORM model, Pydantic schema, or dict
    if isinstance(job, dict):
        title = job.get("title", "Target Role")
        desc = job.get("description", "")
        req_skills = job.get("required_skills", [])
        pref_skills = job.get("preferred_skills", [])
        min_exp = job.get("min_experience_years", 0)
    else:
        title = getattr(job, "title", "Target Role")
        desc = getattr(job, "description", "")
        req_skills = getattr(job, "required_skills", [])
        pref_skills = getattr(job, "preferred_skills", [])
        min_exp = getattr(job, "min_experience_years", 0)

    return active_evaluator.evaluate(
        job_title=title,
        job_description=desc,
        required_skills=req_skills,
        preferred_skills=pref_skills,
        min_experience_years=min_exp,
        candidate_name=candidate_name,
        resume_raw_text=resume_raw_text,
        extracted_skills=extracted_skills,
        extracted_experience_years=extracted_experience_years,
        extracted_education=extracted_education or [],
    )
