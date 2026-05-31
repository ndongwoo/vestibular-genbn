from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any
import csv
import math

from .derived_nodes import evaluate_findings
from .posterior import (
    DiseasePosterior,
    EvidenceContribution,
    inv_logit,
    logit,
    lr_for_observation,
)


def _default_priors(bundle: Any) -> dict[str, float]:
    # Research seed default only. Real use should pass setting-specific priors.
    return {disease_id: 0.10 for disease_id in bundle.active_disease_ids}


def run_case(
    bundle: Any,
    raw_case: dict[str, Any],
    *,
    priors: dict[str, float] | None = None,
    include_inactive: bool = False,
) -> dict[str, Any]:
    """Run one case with independent disease posteriors."""

    priors = dict(priors or _default_priors(bundle))
    values = evaluate_findings(bundle, raw_case)

    # Build a mapping to identify which finding nodes belong to exclusive graded support groups
    finding_to_group = {}
    for finding in bundle.finding_patterns:
        group_type = finding.get("group_type")
        if group_type == "exclusive_graded_support":
            group_id = finding["id"]
            levels = finding.get("levels", [])
            for level in levels:
                finding_to_group[level["node"]] = group_id

    active = set(bundle.active_disease_ids)
    rows_by_disease: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in bundle.likelihood_rows:
        disease = row["disease_node"]
        if include_inactive or disease in active:
            rows_by_disease[disease].append(row)

    posteriors: list[DiseasePosterior] = []

    for disease_id in sorted(rows_by_disease):
        prior = priors.get(disease_id, 0.10)
        current_log_odds = logit(prior)
        contributions: list[EvidenceContribution] = []

        for row in rows_by_disease[disease_id]:
            finding = row["finding_node"]
            observed = values.get(finding, "unknown")
            if observed not in {"yes", "no"}:
                continue

            # Skip likelihood updates for inactive levels in exclusive graded support groups
            # In such groups, "no" values are structural outputs from the priority cascade, not true absence of disease support
            if finding in finding_to_group:
                # This finding is a level of an exclusive graded support group
                # Skip if the value is "no" (inactive level)
                if observed == "no":
                    continue

            lr = lr_for_observation(
                row["p_finding_true_given_disease_true"],
                row["p_finding_true_given_disease_false"],
                observed,
            )
            if lr <= 0:
                continue

            log_lr = math.log(lr)
            current_log_odds += log_lr
            contributions.append(
                EvidenceContribution(
                    finding_node=finding,
                    observed_value=observed,
                    p_finding_true_given_disease_true=row["p_finding_true_given_disease_true"],
                    p_finding_true_given_disease_false=row["p_finding_true_given_disease_false"],
                    likelihood_ratio=lr,
                    log_likelihood_ratio=log_lr,
                    use=row.get("use", "use_directly"),
                )
            )

        posteriors.append(
            DiseasePosterior(
                disease_node=disease_id,
                prior=prior,
                posterior=inv_logit(current_log_odds),
                log_odds=current_log_odds,
                contributions=contributions,
            )
        )

    posteriors.sort(key=lambda x: x.posterior, reverse=True)

    return {
        "case_id": raw_case.get("case_id", raw_case.get("id", "case")),
        "values": values,
        "disease_posteriors": posteriors,
        "posterior_sum": sum(p.posterior for p in posteriors),
        "normalized_across_diseases": False,
    }


def _clean_observed_raw_inputs(raw_case: dict[str, Any]) -> dict[str, Any]:
    """Return non-empty raw inputs for compact detailed JSON output."""

    out: dict[str, Any] = {}
    for key, value in raw_case.items():
        if key in {"case_id", "id"}:
            continue
        if value is None:
            continue
        if isinstance(value, str) and value.strip() == "":
            continue
        out[key] = value
    return out


def _finding_node_ids(bundle: Any) -> list[str]:
    """Return finding node IDs, including levels inside exclusive graded groups."""

    ids: list[str] = []
    seen: set[str] = set()

    for finding in bundle.finding_patterns:
        finding_id = finding.get("id")
        if finding_id and finding_id not in seen:
            ids.append(finding_id)
            seen.add(finding_id)

        for level in finding.get("levels", []):
            level_node = level.get("node")
            if level_node and level_node not in seen:
                ids.append(level_node)
                seen.add(level_node)

    return ids


def result_to_detailed_dict(
    bundle: Any,
    result: dict[str, Any],
    raw_case: dict[str, Any],
    *,
    audits: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Serialize a case result with raw inputs, derived findings, and LR contributions."""

    values = result["values"]

    return {
        "case_id": result["case_id"],
        "raw_inputs": _clean_observed_raw_inputs(raw_case),
        "evaluated_finding_values": {
            finding_id: values.get(finding_id, "unknown")
            for finding_id in _finding_node_ids(bundle)
        },
        "posterior_sum": result["posterior_sum"],
        "normalized_across_diseases": result["normalized_across_diseases"],
        "disease_posteriors": [
            {
                "rank": rank,
                "disease_node": posterior.disease_node,
                "prior": posterior.prior,
                "posterior": posterior.posterior,
                "log_odds": posterior.log_odds,
                "n_contributions": len(posterior.contributions),
                "contributions": [
                    {
                        "finding_node": contribution.finding_node,
                        "observed_value": contribution.observed_value,
                        "p_finding_true_given_disease_true": contribution.p_finding_true_given_disease_true,
                        "p_finding_true_given_disease_false": contribution.p_finding_true_given_disease_false,
                        "likelihood_ratio": contribution.likelihood_ratio,
                        "log_likelihood_ratio": contribution.log_likelihood_ratio,
                        "use": contribution.use,
                    }
                    for contribution in posterior.contributions
                ],
            }
            for rank, posterior in enumerate(result["disease_posteriors"], start=1)
        ],
        "audit_action_flags": audits or {},
    }


def run_cases(bundle: Any, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [run_case(bundle, row) for row in rows]


def load_case_csv(path: str | Path) -> list[dict[str, Any]]:
    with Path(path).open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]


def flatten_result(result: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rank, posterior in enumerate(result["disease_posteriors"], start=1):
        rows.append(
            {
                "case_id": result["case_id"],
                "rank": rank,
                "disease_node": posterior.disease_node,
                "prior": posterior.prior,
                "posterior": posterior.posterior,
                "n_contributions": len(posterior.contributions),
                "normalized_across_diseases": result["normalized_across_diseases"],
            }
        )
    return rows
