from __future__ import annotations

from dataclasses import dataclass, field
import math


@dataclass(slots=True)
class EvidenceContribution:
    finding_node: str
    observed_value: str
    p_finding_true_given_disease_true: float
    p_finding_true_given_disease_false: float
    likelihood_ratio: float
    log_likelihood_ratio: float
    use: str


@dataclass(slots=True)
class DiseasePosterior:
    disease_node: str
    prior: float
    posterior: float
    log_odds: float
    contributions: list[EvidenceContribution] = field(default_factory=list)


def clamp_probability(p: float, eps: float = 1e-6) -> float:
    return min(max(float(p), eps), 1.0 - eps)


def logit(p: float) -> float:
    p = clamp_probability(p)
    return math.log(p / (1.0 - p))


def inv_logit(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def lr_for_observation(p1: float, p0: float, observed_value: str) -> float:
    p1 = clamp_probability(p1)
    p0 = clamp_probability(p0)

    if observed_value == "yes":
        return p1 / p0
    if observed_value == "no":
        return (1.0 - p1) / (1.0 - p0)

    return 1.0
