from __future__ import annotations

from typing import Any


def posterior_map(result: dict[str, Any]) -> dict[str, float]:
    return {p.disease_node: p.posterior for p in result["disease_posteriors"]}


def summarize_audits(bundle: Any, result: dict[str, Any]) -> dict[str, Any]:
    """Return lightweight posterior/audit/action summary."""

    values = result["values"]
    post = posterior_map(result)

    safety_threshold = bundle.posterior_audit_rules.get("threshold_defaults", {}).get(
        "safety_threshold", 0.25
    )
    moderate = bundle.posterior_audit_rules.get("threshold_defaults", {}).get(
        "moderate_posterior", 0.40
    )

    central_alert = (
        values.get("central_neurologic_red_flag_pattern") == "yes"
        or values.get("central_positional_red_flag_pattern") == "yes"
        or post.get("dx_central_positional_mimic", 0.0) >= safety_threshold
        or post.get("dx_central_vestibular_disorder", 0.0) >= safety_threshold
    )

    mri_cpa = (
        values.get("retrocochlear_cpa_iac_pattern") == "yes"
        or post.get("dx_cpa_iac_retrocochlear_mimic", 0.0) >= moderate
        or post.get("dx_cpa_iac_tumor", 0.0) >= moderate
    )

    # Check for PC-BPPV phenotype support
    pc_bppv_moderate = values.get("pc_bppv_positional_phenotype_support_moderate", "no") == "yes"
    pc_bppv_strong = values.get("pc_bppv_positional_phenotype_support_strong", "no") == "yes"

    # Check for HC-BPPV phenotype support
    hc_bppv_moderate = values.get("hc_bppv_roll_test_phenotype_support_moderate", "no") == "yes"
    hc_bppv_strong = values.get("hc_bppv_roll_test_phenotype_support_strong", "no") == "yes"

    repositioning = (
        pc_bppv_moderate
        or pc_bppv_strong
        or hc_bppv_moderate
        or hc_bppv_strong
        or post.get("dx_pc_bppv", 0.0) >= moderate
        or post.get("dx_hc_bppv", 0.0) >= moderate
    )

    return {
        "urgent_central_evaluation_flag": "yes" if central_alert else "no",
        "mri_iac_cpa_consideration_flag": "yes" if mri_cpa else "no",
        "canalith_repositioning_candidate_flag": "yes" if repositioning else "no",
    }
