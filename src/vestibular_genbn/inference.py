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
                    p_finding_true_given_disease_true=row[
                        "p_finding_true_given_disease_true"
                    ],
                    p_finding_true_given_disease_false=row[
                        "p_finding_true_given_disease_false"
                    ],
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
