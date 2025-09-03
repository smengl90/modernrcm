from __future__ import annotations

import yaml


def validate(flow_yaml: str) -> None:
    data = yaml.safe_load(flow_yaml)
    if not isinstance(data, dict) or "steps" not in data:
        raise ValueError("Invalid flow: missing steps")
    steps = data["steps"]
    if not isinstance(steps, list) or not steps:
        raise ValueError("Invalid flow: steps must be non-empty list")

