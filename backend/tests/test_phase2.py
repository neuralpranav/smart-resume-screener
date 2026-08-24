import io
from pypdf import PdfWriter
from app.core.exceptions import FileParsingException
from app.services.parser_service import (
    validate_file,
    extract_text_from_file,
    extract_text_from_txt,
    extract_text_from_pdf,
    extract_candidate_info,
)
from app.services.evaluation_service import evaluate_candidate_resume
from app.schemas.screening import ScreeningResultBase
from app.schemas.job import JobCreate


def test_pdf_parsing_and_extraction():
    """Test text extraction from a valid PDF binary stream."""
    valid_pdf_bytes = b"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj
4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj
5 0 obj << /Length 73 >> stream
BT
/F1 12 Tf
72 712 Td
(Alex Senior Developer Python FastAPI Docker) Tj
ET
endstream
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000222 00000 n 
0000000293 00000 n 
trailer << /Size 6 /Root 1 0 R >>
startxref
416
%%EOF
"""
    extracted = extract_text_from_file(valid_pdf_bytes, "candidate.pdf")
    assert "Alex Senior Developer" in extracted
    assert "FastAPI" in extracted
    assert "Docker" in extracted
    print("[PASS] PDF binary stream extraction test passed!")


def test_txt_parsing_and_extraction():
    """Test text resume parsing and entity extraction."""
    sample_resume = """
    Jane Developer
    Email: jane.developer@example.com
    Phone: (555) 123-4567
    Location: Austin, TX

    SUMMARY
    Senior Full-Stack Engineer with 5+ years of experience designing high-throughput APIs.

    EXPERIENCE
    Lead Python Developer | TechCorp Inc. (2019 - 2024)
    - Architected backend services with Python, FastAPI, and PostgreSQL.
    - Containerized microservices using Docker and orchestrated deployments on AWS.
    - Set up CI/CD pipelines with GitHub Actions.

    EDUCATION
    Bachelor of Science in Computer Science | University of Texas (2015 - 2019)

    SKILLS
    Python, FastAPI, Docker, PostgreSQL, AWS, React, CI/CD, Git
    """
    raw_bytes = sample_resume.encode("utf-8")
    
    # 1. Test text extraction
    extracted = extract_text_from_file(raw_bytes, "jane_resume.txt")
    assert "Jane Developer" in extracted
    assert "FastAPI" in extracted

    # 2. Test candidate info extraction
    info = extract_candidate_info(extracted)
    assert info["full_name"] == "Jane Developer"
    assert info["email"] == "jane.developer@example.com"
    assert info["phone"] == "(555) 123-4567"
    assert info["location"] == "Austin, TX"
    assert "Python" in info["skills"]
    assert "FastAPI" in info["skills"]
    assert "Docker" in info["skills"]
    assert "AWS" in info["skills"]
    assert info["experience_years"] is not None and info["experience_years"] >= 5.0
    assert len(info["education"]) > 0
    print("[PASS] TXT parsing and extraction test passed!")


def test_file_validation_errors():
    """Test error handling for empty, unsupported, or invalid files."""
    # Test unsupported extension
    try:
        validate_file(b"content", "resume.docx")
        assert False, "Should have raised FileParsingException for unsupported format"
    except FileParsingException as exc:
        assert "Unsupported file format" in str(exc)

    # Test empty file
    try:
        validate_file(b"", "resume.pdf")
        assert False, "Should have raised FileParsingException for empty file"
    except FileParsingException as exc:
        assert "is empty" in str(exc)

    # Test invalid PDF bytes
    try:
        extract_text_from_pdf(b"not a real pdf content")
        assert False, "Should have raised FileParsingException for corrupt PDF"
    except FileParsingException:
        pass

    print("[PASS] File validation and error handling test passed!")


def test_rule_based_evaluation_engine():
    """Test evaluation logic, weighted rubric, explainability, and schema compatibility."""
    job = {
        "title": "Senior Backend Engineer",
        "description": "Looking for a seasoned backend engineer with strong Python and cloud skills.",
        "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
        "preferred_skills": ["AWS", "Kubernetes"],
        "min_experience_years": 3,
    }

    # Candidate 1: Strong Match
    cand1_skills = ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS", "Git"]
    cand1_text = "5 years experience in Python, FastAPI, Docker, PostgreSQL, and AWS cloud."
    cand1_edu = ["B.S. in Computer Science"]
    
    result1 = evaluate_candidate_resume(
        job=job,
        candidate_name="Jane Developer",
        resume_raw_text=cand1_text,
        extracted_skills=cand1_skills,
        extracted_experience_years=5.0,
        extracted_education=cand1_edu,
    )

    # Verify score and properties
    assert result1["match_score"] >= 80.0
    assert result1["fit_level"] == "Strong Match"
    assert result1["is_shortlisted"] is True
    assert "FastAPI" in result1["matched_skills"]
    assert "Kubernetes" in result1["missing_skills"]
    assert len(result1["strengths"]) > 0
    assert "Jane Developer" in result1["justification"]

    # Verify compatibility with Pydantic ScreeningResultBase schema
    validated_schema = ScreeningResultBase.model_validate(result1)
    assert validated_schema.match_score == result1["match_score"]

    # Candidate 2: Low Match
    cand2_skills = ["JavaScript", "HTML", "CSS"]
    cand2_text = "Junior frontend developer with 1 year experience in HTML, CSS, JavaScript."
    
    result2 = evaluate_candidate_resume(
        job=job,
        candidate_name="John Junior",
        resume_raw_text=cand2_text,
        extracted_skills=cand2_skills,
        extracted_experience_years=1.0,
        extracted_education=[],
    )

    assert result2["match_score"] < 60.0
    assert result2["is_shortlisted"] is False
    assert "Python" in result2["missing_skills"]
    assert len(result2["weaknesses"]) > 0

    print("[PASS] Evaluation engine test passed!")


if __name__ == "__main__":
    test_pdf_parsing_and_extraction()
    test_txt_parsing_and_extraction()
    test_file_validation_errors()
    test_rule_based_evaluation_engine()
    print("\nALL PHASE 2 TESTS COMPLETED SUCCESSFULLY!")
