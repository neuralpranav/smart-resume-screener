import io
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from app.core.exceptions import FileParsingException

# Curated taxonomy of common technical skills across languages, frameworks, cloud, databases, and tools
SKILL_TAXONOMY = {
    # Programming Languages
    "Python": [r"\bpython\b", r"\bpython3\b"],
    "JavaScript": [r"\bjavascript\b", r"\bjs\b", r"\bes6\b"],
    "TypeScript": [r"\btypescript\b", r"\bts\b"],
    "Java": [r"\bjava\b"],
    "C++": [r"\bc\+\+\b", r"\bcpp\b"],
    "C#": [r"\bc#\b", r"\bcsharp\b"],
    "Go": [r"\bgolang\b", r"\bgo\s+language\b", r"\bgo\b"],
    "Rust": [r"\brust\b"],
    "PHP": [r"\bphp\b"],
    "Ruby": [r"\bruby\b"],
    "SQL": [r"\bsql\b"],
    "HTML": [r"\bhtml5?\b"],
    "CSS": [r"\bcss3?\b", r"\bsass\b", r"\bscss\b"],
    
    # Frameworks & Libraries
    "FastAPI": [r"\bfastapi\b"],
    "Django": [r"\bdjango\b"],
    "Flask": [r"\bflask\b"],
    "React": [r"\breact(?:\.js)?\b"],
    "Next.js": [r"\bnext(?:\.js)?\b"],
    "Vue.js": [r"\bvue(?:\.js)?\b"],
    "Angular": [r"\bangular\b"],
    "Node.js": [r"\bnode(?:\.js)?\b"],
    "Express": [r"\bexpress(?:\.js)?\b"],
    "Spring Boot": [r"\bspring\s*boot\b", r"\bspring\s*framework\b"],
    ".NET": [r"\b\.net\b", r"\basp\.net\b", r"\bdotnet\b"],
    "PyTorch": [r"\bpytorch\b"],
    "TensorFlow": [r"\btensorflow\b"],
    "Pandas": [r"\bpandas\b"],
    "NumPy": [r"\bnumpy\b"],
    "Scikit-Learn": [r"\bscikit-learn\b", r"\bsklearn\b"],

    # Databases
    "PostgreSQL": [r"\bpostgres(?:ql)?\b"],
    "MySQL": [r"\bmysql\b"],
    "MongoDB": [r"\bmongodb\b", r"\bmongo\b"],
    "Redis": [r"\bredis\b"],
    "SQLite": [r"\bsqlite3?\b"],
    "Elasticsearch": [r"\belasticsearch\b"],
    "DynamoDB": [r"\bdynamodb\b"],

    # Cloud, DevOps & Infrastructure
    "AWS": [r"\baws\b", r"\bamazon\s+web\s+services\b"],
    "Azure": [r"\bazure\b", r"\bmicrosoft\s+azure\b"],
    "GCP": [r"\bgcp\b", r"\bgoogle\s+cloud(?:platform)?\b"],
    "Docker": [r"\bdocker\b", r"\bcontainerization\b"],
    "Kubernetes": [r"\bkubernetes\b", r"\bk8s\b"],
    "CI/CD": [r"\bci\/cd\b", r"\bcontinuous\s+integration\b", r"\bgithub\s+actions\b", r"\bjenkins\b"],
    "Terraform": [r"\bterraform\b"],
    "Linux": [r"\blinux\b", r"\bunix\b", r"\bubuntu\b"],
    "Git": [r"\bgit\b", r"\bgithub\b", r"\bgitlab\b"],

    # Architecture & Concepts
    "REST API": [r"\brest(?:ful)?\s*api[s]?\b", r"\brest\b"],
    "GraphQL": [r"\bgraphql\b"],
    "Microservices": [r"\bmicroservices\b", r"\bmicroservice\b"],
    "Agile": [r"\bagile\b", r"\bscrum\b"],
    "Unit Testing": [r"\bunit\s*testing\b", r"\bpytest\b", r"\btest\s*driven\s*development\b", r"\btdd\b"],
}

DEGREE_PATTERNS = [
    r"\b(?:ph\.?d|doctor\s+of\s+philosophy)\b",
    r"\b(?:m\.?s\.?|m\.?tech|master(?:'s)?(?:\s+of\s+science)?)\b",
    r"\b(?:b\.?s\.?|b\.?tech|b\.?e\.?|bachelor(?:'s)?(?:\s+of\s+science|\s+of\s+engineering|\s+of\s+technology)?)\b",
    r"\b(?:associate(?:'s)?\s+degree)\b",
    r"\b(?:diploma\s+in\s+[\w\s]+)\b",
]


def validate_file(file_bytes: bytes, filename: str, max_size_bytes: int = 10 * 1024 * 1024) -> str:
    """
    Validate file extension and content size.
    Returns the file extension ('pdf' or 'txt').
    """
    if not filename or "." not in filename:
        raise FileParsingException("Filename is missing or does not have a valid extension.")

    extension = filename.rsplit(".", 1)[-1].lower()
    if extension not in ["pdf", "txt"]:
        raise FileParsingException(
            f"Unsupported file format '{extension}'. Only PDF (.pdf) and Plain Text (.txt) are supported."
        )

    if not file_bytes or len(file_bytes) == 0:
        raise FileParsingException(f"File '{filename}' is empty.")

    if len(file_bytes) > max_size_bytes:
        raise FileParsingException(
            f"File '{filename}' exceeds maximum allowed size of {max_size_bytes // (1024 * 1024)}MB."
        )

    return extension


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract and normalize text content from PDF bytes using pypdf."""
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception:
                raise FileParsingException("The PDF file is password protected and cannot be read.")

        extracted_pages: List[str] = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                extracted_pages.append(page_text)

        full_text = "\n".join(extracted_pages).strip()
        if not full_text:
            raise FileParsingException(
                "PDF contains no extractable text (it may be a scanned image or empty)."
            )

        return normalize_text(full_text)

    except PdfReadError as err:
        raise FileParsingException(f"Corrupted or invalid PDF file: {str(err)}")
    except FileParsingException:
        raise
    except Exception as err:
        raise FileParsingException(f"Failed to extract text from PDF: {str(err)}")


def extract_text_from_txt(file_bytes: bytes) -> str:
    """Extract and normalize text content from plain text bytes."""
    for encoding in ["utf-8", "latin-1", "cp1252"]:
        try:
            text = file_bytes.decode(encoding).strip()
            if not text:
                raise FileParsingException("Text file contains no readable content.")
            return normalize_text(text)
        except UnicodeDecodeError:
            continue

    raise FileParsingException("Unable to decode text file with standard character encodings.")


def normalize_text(text: str) -> str:
    """Clean unprintable characters and standardize whitespace."""
    # Remove null bytes and carriage returns
    cleaned = text.replace("\x00", "").replace("\r\n", "\n").replace("\r", "\n")
    # Replace multiple spaces with a single space
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    # Standardize repeated blank lines
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """Validate and extract text from an uploaded resume file (PDF or TXT)."""
    file_type = validate_file(file_bytes, filename)
    if file_type == "pdf":
        return extract_text_from_pdf(file_bytes)
    return extract_text_from_txt(file_bytes)


def extract_candidate_name(text: str) -> Optional[str]:
    """Heuristic extraction of candidate full name from resume header."""
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        return None

    # Blacklist words commonly seen in resume headers that aren't personal names
    blacklist = {
        "resume", "curriculum", "vitae", "cv", "page", "email", "phone", "profile",
        "summary", "experience", "education", "skills", "contact", "address", "objective"
    }

    # Inspect top 5 lines
    for line in lines[:5]:
        clean_line = re.sub(r"[^\w\s]", "", line).strip()
        words = clean_line.split()

        # Typical names are 2-4 words, alphabetic, without digits or symbols
        if 2 <= len(words) <= 4:
            if not any(w.lower() in blacklist for w in words):
                if all(w.isalpha() for w in words) and not any(char.isdigit() for char in line):
                    return " ".join(words).title()

    return None


def extract_email(text: str) -> Optional[str]:
    """Extract email address using regex."""
    email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text)
    return email_match.group(0).lower() if email_match else None


def extract_phone(text: str) -> Optional[str]:
    """Extract contact phone number using regex."""
    phone_pattern = r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
    phone_match = re.search(phone_pattern, text)
    return phone_match.group(0).strip() if phone_match else None


def extract_location(text: str) -> Optional[str]:
    """Extract location heuristic (e.g. 'City, State' or 'City, Country')."""
    location_pattern = r"\b([A-Z][a-zA-Z\s]{2,20}),\s*([A-Z]{2}|[A-Z][a-zA-Z\s]{2,15})\b"
    lines = [line.strip() for line in text.split("\n")[:10] if line.strip()]
    for line in lines:
        match = re.search(location_pattern, line)
        if match:
            city, region = match.group(1).strip(), match.group(2).strip()
            # Avoid false positives with skills or degrees
            if not any(w.lower() in ["bachelor", "master", "university", "engineer"] for w in [city, region]):
                return f"{city}, {region}"
    return None


def extract_skills(text: str) -> List[str]:
    """Identify recognized skills from the resume text using taxonomy patterns."""
    matched_skills: List[str] = []
    text_lower = text.lower()

    for canonical_name, patterns in SKILL_TAXONOMY.items():
        for pattern in patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                if canonical_name not in matched_skills:
                    matched_skills.append(canonical_name)
                break

    return matched_skills


def extract_education(text: str) -> List[str]:
    """Extract educational degrees and academic background lines."""
    found_degrees: List[str] = []
    lines = text.split("\n")

    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
        for pattern in DEGREE_PATTERNS:
            if re.search(pattern, line_clean, re.IGNORECASE):
                if len(line_clean) <= 120 and line_clean not in found_degrees:
                    found_degrees.append(line_clean)
                break

    return found_degrees


def extract_experience_years(text: str) -> Optional[float]:
    """
    Estimate total years of professional experience:
    1. Looking for explicit 'X years of experience' statements.
    2. Calculating spans from date ranges (e.g., '2018 - 2023', '2020 - Present').
    """
    current_year = datetime.now().year
    years_found: List[float] = []

    # 1. Explicit experience statements (e.g. "5+ years of experience", "3.5 yrs experience")
    explicit_pattern = r"\b(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+experience\b"
    for match in re.finditer(explicit_pattern, text, re.IGNORECASE):
        try:
            yrs = float(match.group(1))
            if 0 < yrs <= 40:
                years_found.append(yrs)
        except ValueError:
            pass

    # 2. Date ranges (e.g., "2018 - 2022", "2019 - Present", "Jan 2021 to Current")
    date_range_pattern = r"\b(19\d{2}|20\d{2})\s*[-–to]+\s*(19\d{2}|20\d{2}|present|current|now)\b"
    date_spans: List[tuple[int, int]] = []

    for match in re.finditer(date_range_pattern, text, re.IGNORECASE):
        start_year = int(match.group(1))
        end_str = match.group(2).lower()
        end_year = current_year if end_str in ["present", "current", "now"] else int(end_str)

        if 1980 <= start_year <= current_year and start_year <= end_year <= current_year:
            date_spans.append((start_year, end_year))

    if date_spans:
        # Sum non-overlapping or calculate rough total span from earliest to latest
        min_year = min(s[0] for s in date_spans)
        max_year = max(s[1] for s in date_spans)
        span = float(max_year - min_year)
        if 0 < span <= 40:
            years_found.append(span)

    if years_found:
        return round(max(years_found), 1)

    return None


def extract_candidate_info(raw_text: str) -> Dict[str, Any]:
    """
    Extract structured candidate metadata from resume text:
    - Full Name
    - Email
    - Phone
    - Location
    - Extracted Skills
    - Education
    - Approximate Experience in Years
    """
    return {
        "full_name": extract_candidate_name(raw_text) or "Unknown Candidate",
        "email": extract_email(raw_text),
        "phone": extract_phone(raw_text),
        "location": extract_location(raw_text),
        "skills": extract_skills(raw_text),
        "education": extract_education(raw_text),
        "experience_years": extract_experience_years(raw_text),
    }
