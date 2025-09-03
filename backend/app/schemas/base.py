from __future__ import annotations

from pydantic import BaseModel, Field


class APIModel(BaseModel):
    class Config:
        from_attributes = True


class RunCreate(APIModel):
    purpose: str
    payer_id: str
    provider_npi: str | None = None
    input: dict = Field(default_factory=dict)
    idempotency_hints: dict | None = None


class RunOut(APIModel):
    id: str
    purpose: str
    payer_id: str
    provider_npi: str | None
    status: str
    source: str | None
    input: dict | None = None
    output: dict | None = None
    error_code: str | None = None
    error_msg: str | None = None

