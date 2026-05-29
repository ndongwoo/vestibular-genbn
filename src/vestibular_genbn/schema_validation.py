from __future__ import annotations

from typing import Any

from .exceptions import KnowledgeValidationError


def _ids(items: list[dict[str, Any]]) -> set[str]:
    return {str(item["id"]) for item in items}


def validate_bundle(bundle: Any) -> None:
    """Perform lightweight internal-reference validation."""

    errors: list[str] = []

    disease_ids = _ids(bundle.disease_nodes)
    observation_ids = _ids(bundle.observation_nodes)
    finding_ids = _ids(bundle.finding_patterns)
    
    # Add level node IDs from exclusive graded support groups to finding_ids for validation
    for finding in bundle.finding_patterns:
        if finding.get("group_type") == "exclusive_graded_support":
            for level in finding.get("levels", []):
                if "node" in level:
                    finding_ids.add(level["node"])

    for disease in bundle.disease_nodes:
        for field in ("id", "label", "status", "family", "posterior_mode"):
            if field not in disease:
                errors.append(f"disease node missing {field}: {disease}")

    for observation in bundle.observation_nodes:
        for field in ("id", "label", "group", "stage", "value_type", "states"):
            if field not in observation:
                errors.append(f"raw observation missing {field}: {observation}")

    for finding in bundle.finding_patterns:
        # Check for group-type patterns
        group_type = finding.get("group_type")
        if group_type == "exclusive_graded_support":
            # For exclusive graded support groups, don't require rule field but require levels
            for field in ("id", "label", "group_type", "levels", "diagnostic_evidence"):
                if field not in finding:
                    errors.append(f"finding pattern missing {field}: {finding}")
            # Validate levels structure
            if "levels" in finding:
                for i, level in enumerate(finding["levels"]):
                    required_level_fields = ("level", "node", "rule")
                    for field in required_level_fields:
                        if field not in level:
                            errors.append(f"level {i} missing {field}: {level}")
        else:
            # Standard pattern - require rule field
            for field in ("id", "label", "rule_type", "rule", "components", "diagnostic_evidence"):
                if field not in finding:
                    errors.append(f"finding pattern missing {field}: {finding}")
        for component in finding.get("components", []):
            if component not in observation_ids and component not in finding_ids:
                errors.append(f"finding {finding.get('id')} references unknown component {component}")

    for row in bundle.likelihood_rows:
        for field in (
            "disease_node",
            "finding_node",
            "p_finding_true_given_disease_true",
            "p_finding_true_given_disease_false",
            "evidence_quality",
            "use",
        ):
            if field not in row:
                errors.append(f"likelihood row missing {field}: {row}")

        disease = row.get("disease_node")
        finding = row.get("finding_node")
        if disease not in disease_ids:
            errors.append(f"likelihood row references unknown disease node: {disease}")
        if finding not in finding_ids:
            errors.append(f"likelihood row references unknown finding node: {finding}")

        p1 = row.get("p_finding_true_given_disease_true")
        p0 = row.get("p_finding_true_given_disease_false")
        if isinstance(p1, (int, float)) and not 0 <= p1 <= 1:
            errors.append(f"invalid p1 for {disease}/{finding}: {p1}")
        if isinstance(p0, (int, float)) and not 0 <= p0 <= 1:
            errors.append(f"invalid p0 for {disease}/{finding}: {p0}")

    active = set(bundle.active_disease_ids)
    missing_active = active - disease_ids
    if missing_active:
        errors.append(f"candidate set includes unknown active disease nodes: {sorted(missing_active)}")

    policy = bundle.inference_policy.get("posterior_mode")
    if policy != "independent_binary_multilabel":
        errors.append(f"unexpected posterior mode: {policy}")

    normalize = bundle.inference_policy.get("mathematical_policy", {}).get(
        "normalization_across_diseases"
    )
    if normalize != "never":
        errors.append("inference policy must state normalization_across_diseases = never")

    if errors:
        joined = "\n".join(errors)
        raise KnowledgeValidationError(f"Knowledge bundle validation failed:\n{joined}")
