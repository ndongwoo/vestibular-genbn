from __future__ import annotations

from pathlib import Path

from vestibular_genbn import load_knowledge_bundle
from vestibular_genbn.inference import load_case_csv, run_case
from vestibular_genbn.audit import summarize_audits


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    knowledge = repo_root / "knowledge" / "default_v0_1"
    case_file = repo_root / "examples" / "synthetic_cases.csv"

    bundle = load_knowledge_bundle(knowledge)
    cases = load_case_csv(case_file)

    for case in cases:
        result = run_case(bundle, case)
        audits = summarize_audits(bundle, result)
        top = result["disease_posteriors"][0]
        print(
            f"{result['case_id']}: top={top.disease_node} "
            f"posterior={top.posterior:.3f} "
            f"posterior_sum={result['posterior_sum']:.3f} "
            f"normalized={result['normalized_across_diseases']} "
            f"central_alert={audits['urgent_central_evaluation_flag']}"
        )


if __name__ == "__main__":
    main()
