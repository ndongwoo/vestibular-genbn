from __future__ import annotations

from pathlib import Path
import pytest

from vestibular_genbn import load_knowledge_bundle


@pytest.fixture()
def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture()
def knowledge_path(repo_root: Path) -> Path:
    return repo_root / "knowledge" / "default_v0_1"


@pytest.fixture()
def bundle(knowledge_path: Path):
    return load_knowledge_bundle(knowledge_path)
