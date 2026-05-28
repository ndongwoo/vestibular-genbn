def test_load_bundle(bundle):
    assert bundle.manifest["project_id"] == "vestibular_genbn_clean_seed"
    assert len(bundle.disease_nodes) >= 20
    assert len(bundle.observation_nodes) >= 60
    assert len(bundle.finding_patterns) >= 20
    assert len(bundle.likelihood_rows) >= 20


def test_active_nodes_are_independent(bundle):
    assert bundle.candidate_set["posterior_mode"] == "independent_binary_multilabel"
    assert bundle.candidate_set["normalization_across_disease_nodes"] is False
