from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config import settings
from app.core.database import get_db
from app.schemas.common import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse, status_code=status.HTTP_200_OK)
def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    """Verify application uptime and active database connectivity."""
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = f"disconnected: {str(exc)}"

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        version=settings.APP_VERSION,
        database_status=db_status,
        timestamp=datetime.now(timezone.utc),
    )
