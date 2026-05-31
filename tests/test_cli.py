from click.testing import CliRunner
import json

from vestibular_genbn.cli import main


def test_cli_validate(knowledge_path):
    runner = CliRunner()
    result = runner.invoke(main, ["validate", str(knowledge_path)])
    assert result.exit_code == 0
    assert "OK:" in result.output


def test_cli_list_diseases(knowledge_path):
    runner = CliRunner()
    result = runner.invoke(main, ["list-diseases", str(knowledge_path)])
    assert result.exit_code == 0
    assert "dx_pc_bppv" in result.output


def test_cli_json_output_includes_detailed_contributions(knowledge_path, repo_root):
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "run",
            "--case-file",
            str(repo_root / "examples" / "synthetic_cases.csv"),
            "--knowledge",
            str(knowledge_path),
            "--json-output",
        ],
    )

    assert result.exit_code == 0

    data = json.loads(result.output)
    first = data[0]

    assert first["case_id"] == "S01_typical_pc_bppv"
    assert "raw_inputs" in first
    assert "evaluated_finding_values" in first
    assert "disease_posteriors" in first
    assert "audit_action_flags" in first

    pc_bppv = next(p for p in first["disease_posteriors"] if p["disease_node"] == "dx_pc_bppv")

    assert pc_bppv["contributions"]

    contribution = pc_bppv["contributions"][0]
    assert "finding_node" in contribution
    assert "observed_value" in contribution
    assert "p_finding_true_given_disease_true" in contribution
    assert "p_finding_true_given_disease_false" in contribution
    assert "likelihood_ratio" in contribution
    assert "log_likelihood_ratio" in contribution
