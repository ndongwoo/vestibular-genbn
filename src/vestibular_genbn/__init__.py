"""Vestibular-GenBN.

A small executable seed framework for modular generative Bayesian network
knowledge bundles in vestibular diagnostic research.
"""

from .knowledge_loader import KnowledgeBundle, load_knowledge_bundle
from .inference import run_case, run_cases
from .posterior import DiseasePosterior

__version__ = "0.1.2"

__all__ = [
    "KnowledgeBundle",
    "DiseasePosterior",
    "load_knowledge_bundle",
    "run_case",
    "run_cases",
]
