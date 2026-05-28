from pathlib import Path

from vestibular_genbn.inference import load_case_csv, run_case


def test_synthetic_cases_run(bundle, repo_root: Path):
    cases = load_case_csv(repo_root / "examples" / "synthetic_cases.csv")
    assert len(cases) >= 8

    for case in cases:
        result = run_case(bundle, case)
        assert result["disease_posteriors"]
        assert result["normalized_across_diseases"] is False
