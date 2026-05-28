from __future__ import annotations

from typing import Any

from .rule_engine import evaluate_rule, normalize_value


def evaluate_findings(bundle: Any, raw_case: dict[str, Any]) -> dict[str, Any]:
    """Evaluate finding patterns from raw observations."""

    values: dict[str, Any] = {k: normalize_value(v) for k, v in raw_case.items()}
    for obs in bundle.observation_nodes:
        values.setdefault(obs["id"], "unknown")

    # Initialize all findings as unknown.
    for finding in bundle.finding_patterns:
        values.setdefault(finding["id"], "unknown")

    # Iterate because findings can depend on other findings.
    for _ in range(len(bundle.finding_patterns) + 2):
        changed = False
        for finding in bundle.finding_patterns:
            old = values.get(finding["id"], "unknown")
            try:
                result = evaluate_rule(finding["rule"], values)
            except Exception:
                result = None

            new = "yes" if result is True else "no" if result is False else "unknown"
            if new != old:
                values[finding["id"]] = new
                changed = True
        if not changed:
            break

    return values
