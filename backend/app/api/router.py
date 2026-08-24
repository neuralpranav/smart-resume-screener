from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.jobs import router as jobs_router
from app.api.resumes import router as resumes_router
from app.api.screening import router as screening_router

api_router = APIRouter(prefix="/api")

# Register sub-routers
api_router.include_router(health_router)
api_router.include_router(jobs_router)
api_router.include_router(resumes_router)
api_router.include_router(screening_router)
