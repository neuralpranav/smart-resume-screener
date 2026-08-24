from app.core.database import SessionLocal, init_db
from app.api.health import health_check
from app.schemas.job import JobCreate, JobUpdate
from app.schemas.screening import ShortlistToggleRequest
from app.services import job_service, resume_service, screening_service
from app.core.exceptions import NotFoundException, FileParsingException


def setup_module():
    """Ensure database tables are initialized before tests."""
    init_db()


def test_health_check_endpoint():
    """Verify health endpoint database query and response."""
    db = SessionLocal()
    try:
        health = health_check(db=db)
        assert health.status == "healthy"
        assert health.database_status == "connected"
        print("[PASS] Health endpoint verified.")
    finally:
        db.close()


def test_job_crud_workflow():
    """Verify Job Description creation, retrieval, listing, updating, and deletion."""
    db = SessionLocal()
    try:
        # 1. Create Job
        job_in = JobCreate(
            title="Senior Full-Stack Engineer",
            department="Product Engineering",
            description="Seeking an experienced full-stack engineer proficient in Python, FastAPI, and React.",
            required_skills=["Python", "FastAPI", "React", "PostgreSQL"],
            preferred_skills=["Docker", "AWS"],
            min_experience_years=4,
        )
        job = job_service.create_job(db=db, job_in=job_in)
        assert job.id is not None
        assert job.title == "Senior Full-Stack Engineer"
        assert len(job.required_skills) == 4

        # 2. Retrieve Job by ID
        fetched = job_service.get_job(db=db, job_id=job.id)
        assert fetched.id == job.id

        # 3. List Jobs
        jobs_list = job_service.list_jobs(db=db)
        assert any(j.id == job.id for j in jobs_list)

        # 4. Update Job
        update_data = JobUpdate(min_experience_years=5, department="Platform Team")
        updated = job_service.update_job(db=db, job_id=job.id, job_update=update_data)
        assert updated.min_experience_years == 5
        assert updated.department == "Platform Team"

        # 5. Delete Job
        job_service.delete_job(db=db, job_id=job.id)
        try:
            job_service.get_job(db=db, job_id=job.id)
            assert False, "Should raise NotFoundException after deletion"
        except NotFoundException:
            pass

        print("[PASS] Job Description CRUD workflow verified.")
    finally:
        db.close()


def test_resume_upload_and_candidate_linking():
    """Verify resume text extraction, candidate creation/linking, and resume metadata storage."""
    db = SessionLocal()
    try:
        # 1. Upload TXT resume
        txt_resume_content = """
        John Smith
        Email: john.smith@techcorp.io
        Phone: (415) 888-9999
        Location: San Francisco, CA

        SUMMARY
        Senior Backend Architect with 6+ years of experience in distributed systems.

        EXPERIENCE
        Lead Engineer | CloudCorp (2018 - 2024)
        - Built microservices using Python, FastAPI, Docker, and PostgreSQL.
        - Designed cloud infrastructure on AWS and CI/CD pipelines.

        EDUCATION
        B.S. in Computer Science | UC Berkeley

        SKILLS
        Python, FastAPI, Docker, PostgreSQL, AWS, Redis, Git, CI/CD
        """
        resume1 = resume_service.process_and_save_resume(
            db=db,
            file_bytes=txt_resume_content.encode("utf-8"),
            filename="john_smith_resume.txt",
        )
        assert resume1.id is not None
        assert resume1.candidate is not None
        assert resume1.candidate.full_name == "John Smith"
        assert resume1.candidate.email == "john.smith@techcorp.io"
        assert "Python" in resume1.extracted_skills
        assert "FastAPI" in resume1.extracted_skills

        # 2. Upload second resume for same candidate email to test candidate deduplication
        updated_txt = txt_resume_content + "\n- Added Next.js and React expertise."
        resume2 = resume_service.process_and_save_resume(
            db=db,
            file_bytes=updated_txt.encode("utf-8"),
            filename="john_smith_updated.txt",
        )
        # Should link to the same candidate
        assert resume2.candidate_id == resume1.candidate_id

        # 3. Test invalid resume upload error handling
        try:
            resume_service.process_and_save_resume(
                db=db,
                file_bytes=b"",
                filename="empty_resume.txt",
            )
            assert False, "Empty file should raise FileParsingException"
        except FileParsingException:
            pass

        # Clean up
        resume_service.delete_resume(db=db, resume_id=resume1.id)
        resume_service.delete_resume(db=db, resume_id=resume2.id)

        print("[PASS] Resume upload and candidate linking verified.")
    finally:
        db.close()


def test_end_to_end_screening_and_ranking():
    """Verify complete end-to-end flow: Create Job -> Upload Resumes -> Screen -> Rank Leaderboard -> Shortlist Toggle."""
    db = SessionLocal()
    try:
        # Step 1: Create Job Description
        job_in = JobCreate(
            title="Backend Python Developer",
            description="Looking for Python backend developer with FastAPI and SQL expertise.",
            required_skills=["Python", "FastAPI", "SQL"],
            preferred_skills=["Docker", "AWS"],
            min_experience_years=3,
        )
        job = job_service.create_job(db=db, job_in=job_in)

        # Step 2: Upload Resume A (Strong Match)
        resume_a_text = """
        Alice Senior
        Email: alice@example.com
        Phone: 555-0101
        Location: Seattle, WA

        Senior Engineer with 5 years experience in Python, FastAPI, SQL, Docker, and AWS.
        Education: B.S. in Software Engineering
        """
        resume_a = resume_service.process_and_save_resume(
            db=db, file_bytes=resume_a_text.encode("utf-8"), filename="alice.txt"
        )

        # Step 3: Upload Resume B (Junior / Lower Match)
        resume_b_text = """
        Bob Junior
        Email: bob@example.com
        Phone: 555-0202
        Location: Denver, CO

        Junior Web Developer with 1 year experience in HTML, CSS, and JavaScript.
        """
        resume_b = resume_service.process_and_save_resume(
            db=db, file_bytes=resume_b_text.encode("utf-8"), filename="bob.txt"
        )

        # Step 4: Screen Candidate A
        screening_a = screening_service.screen_resume(
            db=db, job_id=job.id, resume_id=resume_a.id
        )
        assert screening_a.match_score >= 75.0
        assert screening_a.fit_level == "Strong Match"
        assert screening_a.is_shortlisted is True
        assert "Python" in screening_a.matched_skills
        assert len(screening_a.strengths) > 0

        # Step 5: Screen Candidate B
        screening_b = screening_service.screen_resume(
            db=db, job_id=job.id, resume_id=resume_b.id
        )
        assert screening_b.match_score < 60.0
        assert screening_b.fit_level != "Strong Match"
        assert "Python" in screening_b.missing_skills

        # Step 6: Get Ranked Leaderboard
        rankings = screening_service.get_ranked_candidates(db=db, job_id=job.id)
        assert len(rankings) == 2
        # Highest match score must be first
        assert rankings[0].candidate_name == "Alice Senior"
        assert rankings[1].candidate_name == "Bob Junior"
        assert rankings[0].match_score > rankings[1].match_score

        # Step 7: Filter Leaderboard by Shortlisted Only
        shortlisted = screening_service.get_ranked_candidates(
            db=db, job_id=job.id, shortlisted_only=True
        )
        assert len(shortlisted) == 1
        assert shortlisted[0].candidate_name == "Alice Senior"

        # Step 8: Manually toggle shortlist for Bob
        updated_b = screening_service.toggle_shortlist(
            db=db, screening_id=screening_b.id, is_shortlisted=True
        )
        assert updated_b.is_shortlisted is True

        # Clean up test artifacts
        resume_service.delete_resume(db=db, resume_id=resume_a.id)
        resume_service.delete_resume(db=db, resume_id=resume_b.id)
        job_service.delete_job(db=db, job_id=job.id)

        print("[PASS] End-to-end screening, ranking, and shortlisting workflow verified.")
    finally:
        db.close()


if __name__ == "__main__":
    setup_module()
    test_health_check_endpoint()
    test_job_crud_workflow()
    test_resume_upload_and_candidate_linking()
    test_end_to_end_screening_and_ranking()
    print("\nALL PHASE 3 WORKFLOW TESTS COMPLETED SUCCESSFULLY!")
