from click.testing import CliRunner

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
