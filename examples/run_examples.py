from __future__ import annotations

from pathlib import Path
import csv
import json

from vestibular_genbn import load_knowledge_bundle
from vestibular_genbn.audit import summarize_audits
from vestibular_genbn.inference import (
    flatten_result,
    load_case_csv,
    result_to_detailed_dict,
    run_case,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    knowledge = repo_root / "knowledge" / "default_v0_1"
    case_file = repo_root / "examples" / "synthetic_cases.csv"

    bundle = load_knowledge_bundle(knowledge)
    cases = load_case_csv(case_file)

    summary_rows: list[dict[str, object]] = []
    detailed_outputs: list[dict[str, object]] = []

    for case in cases:
        result = run_case(bundle, case)
        audits = summarize_audits(bundle, result)

        detailed_outputs.append(result_to_detailed_dict(bundle, result, case, audits=audits))

        for row in flatten_result(result):
            row.update(audits)
            summary_rows.append(row)

    summary_path = repo_root / "examples" / "output_core_v0_1.csv"
    details_path = repo_root / "examples" / "output_core_v0_1_detailed.json"

    if not summary_rows:
        raise RuntimeError("No summary rows were generated.")

    with summary_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(summary_rows)

    details_path.write_text(
        json.dumps(detailed_outputs, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Wrote {summary_path}")
    print(f"Wrote {details_path}")


if __name__ == "__main__":
    main()
