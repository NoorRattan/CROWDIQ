from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import uuid


class ActivateEmergencyRequest(BaseModel):
    venue_id: uuid.UUID
    emergency_type: str
    message: str = Field(min_length=10, max_length=500)
    affected_zones: list[str] = Field(default_factory=list)
    confirmed: bool

    @field_validator("emergency_type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        valid = ["FIRE", "MEDICAL", "SECURITY", "WEATHER", "GENERAL"]
        if v not in valid:
            raise ValueError(f"Type must be one of {valid}")
        return v

    @field_validator("confirmed")
    @classmethod
    def validate_confirmed(cls, v: bool) -> bool:
        if v is not True:
            raise ValueError("confirmed must be True")
        return v


class BlockExitRequest(BaseModel):
    zone_id: uuid.UUID
    is_blocked: bool


class DeactivateEmergencyRequest(BaseModel):
    venue_id: uuid.UUID = Field(description="Venue UUID for the active emergency")
    confirmed: bool = Field(description="Explicit confirmation to deactivate")

    @field_validator("confirmed")
    @classmethod
    def validate_confirmed(cls, v: bool) -> bool:
        if v is not True:
            raise ValueError("confirmed must be True")
        return v


class EmergencyMessageRequest(BaseModel):
    message: str = Field(min_length=5, max_length=500)


class SOSReportRequest(BaseModel):
    venue_id: uuid.UUID
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    message: str | None = Field(default=None, max_length=200)


class SafeConfirmationRequest(BaseModel):
    venue_id: uuid.UUID
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)


class EmergencyStatusResponse(BaseModel):
    """Emergency status for a venue. Returned even when no emergency is active."""

    venue_id: str
    is_active: bool
    emergency_type: str | None = None
    message: str | None = None
    affected_zones: list[str] = Field(default_factory=list)
    activated_at: datetime | None = None
    activated_by_email: str | None = None
    sos_reports_count: int = 0
    evacuation_routes_ready: bool = False


class DeactivateResponse(BaseModel):
    success: bool
    message: str
    incident_id: uuid.UUID
    duration_minutes: int
