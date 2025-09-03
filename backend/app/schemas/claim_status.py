from __future__ import annotations

from pydantic import BaseModel


class ClaimStatusInput(BaseModel):
    payer_id: str
    provider_npi: str
    claim_id: str | None = None
    patient_last_name: str | None = None
    patient_dob: str | None = None
    from_date: str
    to_date: str


class ClaimStatusResponse(BaseModel):
    correlation_id: str
    status: str
    paid_amount: float | None = None
    denials: list[dict] | None = None
    last_update: str | None = None
    source: str
    trace_id: str

