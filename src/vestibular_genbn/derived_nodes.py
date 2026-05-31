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

    # Evaluate exclusive graded support groups
    for finding in bundle.finding_patterns:
        if finding.get("group_type") == "exclusive_graded_support":
            evaluate_exclusive_graded_support_group(finding, values)

    # Iterate because findings can depend on other findings.
    for _ in range(len(bundle.finding_patterns) + 2):
        changed = False
        for finding in bundle.finding_patterns:
            # Skip already processed exclusive graded support groups
            if finding.get("group_type") == "exclusive_graded_support":
                continue

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


def evaluate_exclusive_graded_support_group(
    finding: dict[str, Any], values: dict[str, Any]
) -> None:
    """Evaluate an exclusive graded support group."""
    # For exclusive graded support, evaluate in order of strength
    # strong first, then moderate, then weak
    levels = finding.get("levels", [])

    # Initialize all levels as "no"
    for level in levels:
        level_id = level["node"]
        values[level_id] = "no"

    # Evaluate strong first
    strong_level = None
    for level in levels:
        if level["level"] == "strong":
            strong_level = level
            break

    if strong_level:
        try:
            strong_result = evaluate_rule(strong_level["rule"], values)
        except Exception:
            strong_result = None

        if strong_result is True:
            values[strong_level["node"]] = "yes"
            # Set moderate and weak to "no" since strong overrides them
            for level in levels:
                if level["level"] in ("moderate", "weak"):
                    values[level["node"]] = "no"
            return

    # Evaluate moderate if strong is not true
    moderate_level = None
    for level in levels:
        if level["level"] == "moderate":
            moderate_level = level
            break

    if moderate_level:
        try:
            moderate_result = evaluate_rule(moderate_level["rule"], values)
        except Exception:
            moderate_result = None

        if moderate_result is True:
            values[moderate_level["node"]] = "yes"
            # Set weak to "no" since moderate overrides it
            for level in levels:
                if level["level"] == "weak":
                    values[level["node"]] = "no"
            return

    # Evaluate weak if neither strong nor moderate are true
    weak_level = None
    for level in levels:
        if level["level"] == "weak":
            weak_level = level
            break

    if weak_level:
        try:
            weak_result = evaluate_rule(weak_level["rule"], values)
        except Exception:
            weak_result = None

        if weak_result is True:
            values[weak_level["node"]] = "yes"
            return

    # If none are true, all levels are "no" (already set above)
