from __future__ import annotations

from copy import deepcopy
from typing import Any

from .inference import run_case


def one_way_likelihood_sensitivity(
    bundle: Any,
    raw_case: dict[str, Any],
    *,
    disease_node: str,
    finding_node: str,
    p1_values: list[float],
) -> list[dict[str, float | str]]:
    """Simple one-way sensitivity analysis over P(finding|disease)."""

    output = []
    for p1 in p1_values:
        b = deepcopy(bundle)
        for row in b.likelihood_table["likelihood_rows"]:
            if row["disease_node"] == disease_node and row["finding_node"] == finding_node:
                row["p_finding_true_given_disease_true"] = p1
        result = run_case(b, raw_case)
        posterior = next(
            p.posterior for p in result["disease_posteriors"] if p.disease_node == disease_node
        )
        output.append(
            {
                "disease_node": disease_node,
                "finding_node": finding_node,
                "p1": p1,
                "posterior": posterior,
            }
        )
    return output
