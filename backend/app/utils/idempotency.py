from __future__ import annotations

import hashlib
import json
from typing import Any


def idempotency_key(purpose: str, payer_id: str, provider_npi: str | None, business: dict[str, Any], business_date: str | None = None) -> str:
    parts = {
        "purpose": purpose,
        "payer_id": payer_id,
        "provider_npi": provider_npi,
        "business": business,
        "business_date": business_date,
    }
    payload = json.dumps(parts, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()

