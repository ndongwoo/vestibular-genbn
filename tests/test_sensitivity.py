from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from vestibular_genbn.inference import load_case_csv
from vestibular_genbn.sensitivity import one_way_likelihood_sensitivity


def _load_sensitivity_config(repo_root: Path) -> dict[str, Any]:
    path = repo_root / "knowledge" / "default_v0_1" / "config" / "sensitivity_ranges.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_sensitivity_ranges_config_is_well_formed(repo_root, bundle):
    config = _load_sensitivity_config(repo_root)

    assert config["schema_version"] == "sensitivity_ranges_v0_1"
    assert config["analysis_type"] == "one_way_likelihood_sensitivity"
    assert config["parameters"]

    likelihood_pairs = {
        (row["disease_node"], row["finding_node"]) for row in bundle.likelihood_rows
    }

    for parameter in config["parameters"]:
        assert parameter["parameter"] == "p_finding_true_given_disease_true"
        assert (parameter["disease_node"], parameter["finding_node"]) in likelihood_pairs

        default = parameter["default"]
        p0_fixed_at = parameter["p0_fixed_at"]
        p1_values = parameter["p1_values"]

        assert 0.0 < default < 1.0
        assert 0.0 < p0_fixed_at < 1.0
        assert len(p1_values) >= 2
        assert p1_values == sorted(p1_values)
        assert min(p1_values) <= default <= max(p1_values)
        assert all(0.0 < value < 1.0 for value in p1_values)
        assert parameter["evidence_quality"]
        assert parameter["rationale"]


def test_one_way_likelihood_sensitivity_uses_configured_values(repo_root, bundle):
    config = _load_sensitivity_config(repo_root)
    parameter = next(
        item for item in config["parameters"] if item["id"] == "pc_bppv_moderate_support_p1"
    )
    case = next(
        row
        for row in load_case_csv(repo_root / "examples" / "synthetic_cases.csv")
        if row["case_id"] == "S01_typical_pc_bppv"
    )

    rows = one_way_likelihood_sensitivity(
        bundle,
        case,
        disease_node=parameter["disease_node"],
        finding_node=parameter["finding_node"],
        p1_values=parameter["p1_values"],
    )

    assert [row["p1"] for row in rows] == parameter["p1_values"]
    assert all(row["disease_node"] == "dx_pc_bppv" for row in rows)
    assert all(
        row["finding_node"] == "pc_bppv_positional_phenotype_support_moderate" for row in rows
    )

    posteriors = [row["posterior"] for row in rows]
    assert posteriors == sorted(posteriors)
    assert posteriors[0] < posteriors[-1]
