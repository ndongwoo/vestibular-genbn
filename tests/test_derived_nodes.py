from vestibular_genbn.derived_nodes import evaluate_findings


def test_typical_pc_pattern(bundle):
    case = {
        "hx_recurrent_positional_vertigo": "yes",
        "hx_positional_trigger": "yes",
        "hx_brief_seconds_to_minutes": "yes",
        "dix_hallpike_performed": "yes",
        "dh_torsional_upbeating_nystagmus": "yes",
        "dh_duration_less_than_60s": "yes",
    }
    values = evaluate_findings(bundle, case)
    assert values["typical_positional_history"] == "yes"
    assert values["typical_pc_bppv_pattern"] == "yes"


def test_md_auditory_pattern(bundle):
    case = {
        "hx_two_or_more_vertigo_episodes": "yes",
        "hx_spontaneous_vertigo": "yes",
        "hx_episode_duration_20min_to_24h": "yes",
        "hx_tinnitus_affected_ear": "yes",
        "hx_aural_symptom_temporal_relation_to_vertigo": "yes",
        "affected_ear_laterality": "left",
    }
    values = evaluate_findings(bundle, case)
    assert values["md_probable_duration_pattern"] == "yes"
    assert values["md_fluctuating_aural_symptom_pattern"] == "yes"
