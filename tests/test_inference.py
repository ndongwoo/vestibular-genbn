from vestibular_genbn.inference import run_case


def test_pc_bppv_case_has_pc_posterior(bundle):
    result = run_case(
        bundle,
        {
            "case_id": "pc",
            "hx_recurrent_positional_vertigo": "yes",
            "hx_positional_trigger": "yes",
            "hx_brief_seconds_to_minutes": "yes",
            "dix_hallpike_performed": "yes",
            "dh_torsional_upbeating_nystagmus": "yes",
            "dh_duration_less_than_60s": "yes",
        },
    )
    posterior = {p.disease_node: p.posterior for p in result["disease_posteriors"]}
    assert posterior["dx_pc_bppv"] > posterior["dx_meniere_disease"]


def test_meniere_case_has_md_posterior(bundle):
    result = run_case(
        bundle,
        {
            "case_id": "md",
            "hx_two_or_more_vertigo_episodes": "yes",
            "hx_spontaneous_vertigo": "yes",
            "hx_episode_duration_20min_to_12h": "yes",
            "hx_episode_duration_20min_to_24h": "yes",
            "hx_fluctuating_hearing_loss": "yes",
            "hx_tinnitus_affected_ear": "yes",
            "hx_aural_symptom_temporal_relation_to_vertigo": "yes",
            "affected_ear_laterality": "left",
            "audiometry_performed": "yes",
            "audiometry_low_mid_freq_snhl_affected_ear": "yes",
        },
    )
    posterior = {p.disease_node: p.posterior for p in result["disease_posteriors"]}
    assert posterior["dx_meniere_disease"] > posterior["dx_pc_bppv"]
