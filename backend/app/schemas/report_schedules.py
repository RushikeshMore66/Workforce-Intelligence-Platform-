from datetime import datetime
from typing import Optional
import zoneinfo

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.report_schedule import ReportFormatEnum, ReportFrequencyEnum, ReportTypeEnum
from app.models.report_run import ReportRunStatusEnum, TriggerTypeEnum


class ReportScheduleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    report_type: ReportTypeEnum
    scope_id: Optional[str] = None
    export_format: ReportFormatEnum
    frequency: ReportFrequencyEnum
    timezone: str
    next_run_at: datetime

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        try:
            zoneinfo.ZoneInfo(v)
        except Exception:
            raise ValueError(f"Invalid timezone: {v}")
        return v

    @field_validator("next_run_at")
    @classmethod
    def validate_next_run_at(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("next_run_at must be timezone-aware")
        # Normalize to UTC
        return v.astimezone(zoneinfo.ZoneInfo("UTC"))


class ReportScheduleCreate(ReportScheduleBase):
    pass


class ReportScheduleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    export_format: Optional[ReportFormatEnum] = None
    frequency: Optional[ReportFrequencyEnum] = None
    timezone: Optional[str] = None
    next_run_at: Optional[datetime] = None

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            try:
                zoneinfo.ZoneInfo(v)
            except Exception:
                raise ValueError(f"Invalid timezone: {v}")
        return v

    @field_validator("next_run_at")
    @classmethod
    def validate_next_run_at(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None:
            if v.tzinfo is None:
                raise ValueError("next_run_at must be timezone-aware")
            return v.astimezone(zoneinfo.ZoneInfo("UTC"))
        return v


class ReportScheduleOut(ReportScheduleBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    is_active: bool
    created_by_user_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    @field_validator("next_run_at", mode="before")
    @classmethod
    def ensure_tz_aware(cls, v):
        if isinstance(v, datetime) and v.tzinfo is None:
            return v.replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
        return v


class ReportScheduleListItem(ReportScheduleOut):
    pass


class ReportRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    schedule_id: str
    status: ReportRunStatusEnum
    trigger_type: TriggerTypeEnum
    scheduled_for: Optional[datetime]
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    error_message: Optional[str]
    retry_count: int
    output_filename: Optional[str]
    created_at: datetime
