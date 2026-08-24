from datetime import datetime
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(default="healthy", description="Application health status")
    version: str = Field(..., description="Application version")
    database_status: str = Field(..., description="Database connection status")
    timestamp: datetime = Field(..., description="Current server UTC timestamp")


class MessageResponse(BaseModel):
    message: str
    details: dict = Field(default_factory=dict)
