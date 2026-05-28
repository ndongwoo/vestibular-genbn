from __future__ import annotations

from typing import Any
import networkx as nx


def build_knowledge_graph(bundle: Any) -> nx.DiGraph:
    """Build a lightweight NetworkX graph from the knowledge bundle."""

    graph = nx.DiGraph()

    for obs in bundle.observation_nodes:
        graph.add_node(obs["id"], kind="raw_observation", label=obs.get("label", obs["id"]))

    for finding in bundle.finding_patterns:
        graph.add_node(finding["id"], kind="finding", label=finding.get("label", finding["id"]))
        for component in finding.get("components", []):
            graph.add_edge(component, finding["id"], kind="component")

    for disease in bundle.disease_nodes:
        graph.add_node(disease["id"], kind="disease", label=disease.get("label", disease["id"]))

    for row in bundle.likelihood_rows:
        graph.add_edge(row["finding_node"], row["disease_node"], kind="likelihood")

    return graph


def export_mermaid(bundle: Any) -> str:
    graph = build_knowledge_graph(bundle)
    lines = ["flowchart LR"]
    for source, target, data in graph.edges(data=True):
        lines.append(f"  {source} -->|{data.get('kind', '')}| {target}")
    return "\n".join(lines)
