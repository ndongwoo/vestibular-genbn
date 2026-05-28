from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json

from .schema_validation import validate_bundle


@dataclass(slots=True)
class KnowledgeBundle:
    """Loaded knowledge bundle."""

    root: Path
    manifest: dict[str, Any]
    inference_policy: dict[str, Any]
    candidate_set: dict[str, Any]
    disease_registry: dict[str, Any]
    observation_registry: dict[str, Any]
    finding_registry: dict[str, Any]
    likelihood_table: dict[str, Any]
    criteria_audit_rules: dict[str, Any]
    posterior_audit_rules: dict[str, Any]
    safety_action_rules: dict[str, Any]

    @property
    def disease_nodes(self) -> list[dict[str, Any]]:
        return list(self.disease_registry.get("disease_nodes", []))

    @property
    def active_disease_ids(self) -> list[str]:
        return list(self.candidate_set.get("active_disease_nodes", []))

    @property
    def observation_nodes(self) -> list[dict[str, Any]]:
        return list(self.observation_registry.get("raw_observation_nodes", []))

    @property
    def finding_patterns(self) -> list[dict[str, Any]]:
        return list(self.finding_registry.get("finding_patterns", []))

    @property
    def likelihood_rows(self) -> list[dict[str, Any]]:
        return list(self.likelihood_table.get("likelihood_rows", []))


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_knowledge_bundle(root: str | Path, *, validate: bool = True) -> KnowledgeBundle:
    """Load a knowledge bundle directory."""

    root = Path(root)
    bundle = KnowledgeBundle(
        root=root,
        manifest=_read_json(root / "project_manifest.json"),
        inference_policy=_read_json(root / "config" / "inference_policy_v0_1.json"),
        candidate_set=_read_json(root / "config" / "candidate_set_core_v0_1.json"),
        disease_registry=_read_json(root / "registries" / "disease_node_registry.json"),
        observation_registry=_read_json(root / "registries" / "global_observation_registry.json"),
        finding_registry=_read_json(root / "registries" / "global_finding_pattern_registry.json"),
        likelihood_table=_read_json(root / "likelihoods" / "bppv_meniere_seed_likelihoods.json"),
        criteria_audit_rules=_read_json(root / "audits" / "criteria_audit_rules.json"),
        posterior_audit_rules=_read_json(root / "audits" / "posterior_audit_rules.json"),
        safety_action_rules=_read_json(root / "audits" / "safety_action_rules.json"),
    )

    if validate:
        validate_bundle(bundle)

    return bundle
