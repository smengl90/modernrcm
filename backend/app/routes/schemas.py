from __future__ import annotations

from fastapi import APIRouter
from pydantic import TypeAdapter

from ..schemas.eligibility import EligibilityInput, EligibilityResponse
from ..schemas.claim_status import ClaimStatusInput, ClaimStatusResponse


router = APIRouter()


def schema_of(model):
    ta = TypeAdapter(model)
    return ta.json_schema()


@router.get("/schemas")
async def list_schemas():
    return {
        "EligibilityInput": schema_of(EligibilityInput),
        "EligibilityResponse": schema_of(EligibilityResponse),
        "ClaimStatusInput": schema_of(ClaimStatusInput),
        "ClaimStatusResponse": schema_of(ClaimStatusResponse),
    }

