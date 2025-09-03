from __future__ import annotations

from pydantic import BaseModel, Field


class EligibilityInput(BaseModel):
    payer_id: str
    provider_npi: str
    member_id: str
    patient_last_name: str
    patient_first_name: str | None = None
    patient_dob: str
    service_date: str
    service_type_code: str | None = None


class EligibilityResponse(BaseModel):
    correlation_id: str
    member_id: str
    payer: str
    plan_name: str | None = None
    coverage: dict = Field(default_factory=dict)
    copay: dict | None = None
    deductible: dict | None = None
    as_of: str
    source: str
    trace_id: str

