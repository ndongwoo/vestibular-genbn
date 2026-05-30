from __future__ import annotations

from pathlib import Path
import csv
import json
import click

from .knowledge_loader import load_knowledge_bundle
from .inference import load_case_csv, run_case, flatten_result
from .audit import summarize_audits
from .visualization import export_mermaid
from . import __version__


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    """Vestibular-GenBN command-line interface."""


@main.command()
def version() -> None:
    """Display the version of Vestibular-GenBN."""
    click.echo(__version__)


@main.command()
@click.argument("knowledge", type=click.Path(exists=True, file_okay=False, path_type=Path))
def validate(knowledge: Path) -> None:
    """Validate a knowledge bundle."""

    bundle = load_knowledge_bundle(knowledge, validate=True)
    click.echo(f"OK: {knowledge}")
    click.echo(f"Disease nodes: {len(bundle.disease_nodes)}")
    click.echo(f"Active disease nodes: {len(bundle.active_disease_ids)}")
    click.echo(f"Raw observations: {len(bundle.observation_nodes)}")
    click.echo(f"Finding patterns: {len(bundle.finding_patterns)}")
    click.echo(f"Likelihood rows: {len(bundle.likelihood_rows)}")


@main.command()
@click.option("--case-file", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--knowledge", required=True, type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--output", required=False, type=click.Path(path_type=Path))
@click.option("--json-output", is_flag=True, help="Print JSON result instead of table-like rows.")
def run(case_file: Path, knowledge: Path, output: Path | None, json_output: bool) -> None:
    """Run independent posterior inference for CSV cases."""

    bundle = load_knowledge_bundle(knowledge, validate=True)
    cases = load_case_csv(case_file)

    all_rows = []
    json_results = []
    for case in cases:
        result = run_case(bundle, case)
        audits = summarize_audits(bundle, result)
        json_results.append(
            {
                "case_id": result["case_id"],
                "posterior_sum": result["posterior_sum"],
                "normalized_across_diseases": result["normalized_across_diseases"],
                "disease_posteriors": [
                    {
                        "disease_node": p.disease_node,
                        "prior": p.prior,
                        "posterior": p.posterior,
                        "n_contributions": len(p.contributions),
                    }
                    for p in result["disease_posteriors"]
                ],
                "audits": audits,
            }
        )

        for row in flatten_result(result):
            row.update(audits)
            all_rows.append(row)

    if json_output:
        click.echo(json.dumps(json_results, ensure_ascii=False, indent=2))
        return

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
            writer.writeheader()
            writer.writerows(all_rows)
        click.echo(f"Wrote {output}")
    else:
        for row in all_rows:
            click.echo(
                f"{row['case_id']}\t{row['rank']}\t{row['disease_node']}\t"
                f"{row['posterior']:.3f}\tnormalized={row['normalized_across_diseases']}"
            )


@main.command("list-diseases")
@click.argument("knowledge", type=click.Path(exists=True, file_okay=False, path_type=Path))
def list_diseases(knowledge: Path) -> None:
    """List disease nodes."""

    bundle = load_knowledge_bundle(knowledge)
    for node in bundle.disease_nodes:
        status = node.get("status", "")
        click.echo(f"{node['id']}\t{status}\t{node.get('label', '')}")


@main.command("export-network")
@click.argument("knowledge", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--output", required=False, type=click.Path(path_type=Path))
def export_network(knowledge: Path, output: Path | None) -> None:
    """Export the knowledge graph as a Mermaid flowchart."""

    bundle = load_knowledge_bundle(knowledge)
    text = export_mermaid(bundle)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
        click.echo(f"Wrote {output}")
    else:
        click.echo(text)


if __name__ == "__main__":
    main()
