import pytest

from vestibular_genbn.inference import run_case


def test_posteriors_are_not_normalized_to_one(bundle):
    result = run_case(
        bundle,
        {
            "case_id": "mixed",
            "hx_recurrent_positional_vertigo": "yes",
            "hx_positional_trigger": "yes",
            "hx_brief_seconds_to_minutes": "yes",
            "dix_hallpike_performed": "yes",
            "dh_torsional_upbeating_nystagmus": "yes",
            "hx_two_or_more_vertigo_episodes": "yes",
            "hx_spontaneous_vertigo": "yes",
            "hx_tinnitus_affected_ear": "yes",
            "affected_ear_laterality": "left",
        },
    )
    assert result["normalized_across_diseases"] is False
    assert result["posterior_sum"] != pytest.approx(1.0)
