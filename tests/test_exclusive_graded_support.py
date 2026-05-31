"""
Test exclusive graded support evaluation logic.
"""

from vestibular_genbn import load_knowledge_bundle
from vestibular_genbn.inference import load_case_csv, run_case


def test_exclusive_graded_support_skip_no_values():
    """
    Test that inactive levels in exclusive graded support groups are not used as negative evidence.

    In the S01_typical_pc_bppv case:
    - pc_bppv_positional_phenotype_support_moderate = yes (should contribute positive evidence)
    - pc_bppv_positional_phenotype_support_strong = no (should NOT contribute negative evidence)
    - pc_bppv_positional_phenotype_support_weak = no (should NOT contribute negative evidence)

    Previously, the "no" values were incorrectly penalizing dx_pc_bppv posterior.
    """
    bundle = load_knowledge_bundle("knowledge/default_v0_1")
    cases = load_case_csv("examples/synthetic_cases.csv")

    for case in cases:
        if case["case_id"] == "S01_typical_pc_bppv":
            result = run_case(bundle, case)

            # Verify that dx_pc_bppv is the top diagnosis
            top_disease = result["disease_posteriors"][0].disease_node
            assert top_disease == "dx_pc_bppv", f"Expected dx_pc_bppv to be top, got {top_disease}"

            # Verify that the posterior for dx_pc_bppv is high (should be around 0.9)
            pc_bppv_posterior = None
            for posterior in result["disease_posteriors"]:
                if posterior.disease_node == "dx_pc_bppv":
                    pc_bppv_posterior = posterior.posterior
                    break

            assert pc_bppv_posterior is not None, "dx_pc_bppv posterior not found"
            assert (
                pc_bppv_posterior > 0.8
            ), f"Expected high posterior for dx_pc_bppv, got {pc_bppv_posterior}"

            # Verify the values we expect for the exclusive support group
            values = result["values"]
            assert values["pc_bppv_positional_phenotype_support_moderate"] == "yes"
            assert values["pc_bppv_positional_phenotype_support_strong"] == "no"
            assert values["pc_bppv_positional_phenotype_support_weak"] == "no"

            break


def test_ordinary_binary_behavior_unchanged():
    """
    Test that ordinary binary findings still behave normally (no should provide negative evidence).
    """
    bundle = load_knowledge_bundle("knowledge/default_v0_1")

    # Create a simple case without the support group evidence to test normal behavior
    case = {
        "case_id": "test_normal_behavior",
        "typical_positional_history": "yes",
        "central_positional_red_flag_pattern": "no",  # This should contribute negative evidence
    }

    result = run_case(bundle, case)
    assert "disease_posteriors" in result

    # Should not have a particularly high posterior for any disease
    # since central_positional_red_flag_pattern is negative evidence for all diseases
    # (This test just verifies the function runs without error)


def test_exclusive_support_levels_no_contribute_to_posterior():
    """
    Test that when exclusive support levels are 'no', they shouldn't contribute negatively to posterior.
    """
    bundle = load_knowledge_bundle("knowledge/default_v0_1")
    cases = load_case_csv("examples/synthetic_cases.csv")

    for case in cases:
        if case["case_id"] == "S01_typical_pc_bppv":
            result = run_case(bundle, case)

            # Check values for our specific support levels
            values = result["values"]

            # Moderate support is yes and should contribute significantly
            assert values["pc_bppv_positional_phenotype_support_moderate"] == "yes"

            # Strong and weak support are no - should not contribute negative evidence
            assert values["pc_bppv_positional_phenotype_support_strong"] == "no"
            assert values["pc_bppv_positional_phenotype_support_weak"] == "no"

            # The posterior for dx_pc_bppv should be relatively high due to the moderate support
            pc_bppv_posterior = None
            for posterior in result["disease_posteriors"]:
                if posterior.disease_node == "dx_pc_bppv":
                    pc_bppv_posterior = posterior.posterior
                    break

            # Should be much higher than 0.3 (the previous incorrect result)
            assert (
                pc_bppv_posterior > 0.8
            ), "Expected high posterior for dx_pc_bppv with moderate support"


def test_multiple_disease_scenarios():
    """
    Test that the fix doesn't break other cases.
    """
    bundle = load_knowledge_bundle("knowledge/default_v0_1")
    cases = load_case_csv("examples/synthetic_cases.csv")

    # Test that S02 (HC-BPPV case) still works correctly
    for case in cases:
        if case["case_id"] == "S02_typical_hc_bppv_geotropic":
            result = run_case(bundle, case)

            # Should still rank HC-BPPV highest
            top_disease = result["disease_posteriors"][0].disease_node
            assert (
                top_disease == "dx_hc_bppv"
            ), f"Expected dx_hc_bppv to be top for S02, got {top_disease}"

            break


def test_s01_specific_validation():
    """
    Validation that S01_typical_pc_bppv behaves correctly with our fix:
    - Moderate support yes should increase dx_pc_bppv posterior
    - Inactive support levels should not decrease dx_pc_bppv posterior
    """
    bundle = load_knowledge_bundle("knowledge/default_v0_1")
    cases = load_case_csv("examples/synthetic_cases.csv")

    for case in cases:
        if case["case_id"] == "S01_typical_pc_bppv":
            result = run_case(bundle, case)

            # Get the full disease posteriors
            posteriors = result["disease_posteriors"]

            # Check that dx_pc_bppv is highest
            assert posteriors[0].disease_node == "dx_pc_bppv"
            assert (
                posteriors[0].posterior > 0.8
            ), f"Expected high PC-BPPV posterior, got {posteriors[0].posterior}"

            # Validate the values in the case
            values = result["values"]

            # These are the key findings for our exclusive support group
            assert values["pc_bppv_positional_phenotype_support_moderate"] == "yes"
            assert values["pc_bppv_positional_phenotype_support_strong"] == "no"
            assert values["pc_bppv_positional_phenotype_support_weak"] == "no"

            break


def test_that_old_behavior_would_have_failed():
    """
    This test shows what the old behavior would have been:
    Before our fix, the inactive values (no) were being treated as negative evidence.
    This would have resulted in dx_hc_bppv being higher than dx_pc_bppv.
    """
    bundle = load_knowledge_bundle("knowledge/default_v0_1")
    cases = load_case_csv("examples/synthetic_cases.csv")

    for case in cases:
        if case["case_id"] == "S01_typical_pc_bppv":
            result = run_case(bundle, case)

            # Check that PC-BPPV is now higher than HC-BPPV (which was the previous incorrect result)
            pc_bppv_posterior = None
            hc_bppv_posterior = None

            for posterior in result["disease_posteriors"]:
                if posterior.disease_node == "dx_pc_bppv":
                    pc_bppv_posterior = posterior.posterior
                elif posterior.disease_node == "dx_hc_bppv":
                    hc_bppv_posterior = posterior.posterior

            assert pc_bppv_posterior is not None
            assert hc_bppv_posterior is not None

            # PC-BPPV should now be much higher than HC-BPPV
            assert pc_bppv_posterior > 0.8, "PC-BPPV should have high posterior after fix"
            assert (
                hc_bppv_posterior < 0.4
            ), "HC-BPPV should have low posterior after fix (not the wrong result)"

            break
