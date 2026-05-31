# Evidence-to-likelihood mapping

This document describes how literature-derived and expert-informed diagnostic evidence is converted into seed likelihood parameters for Vestibular-GenBN knowledge bundles.

Vestibular-GenBN uses conservative, transparent, and editable likelihood parameters. These values are intended for software demonstration, knowledge engineering, and sensitivity analysis. They are not clinically validated calibration parameters.

## Generative likelihood scale

For each disease node and finding node pair, the likelihood table stores two conditional probabilities:

```text
p1 = P(finding = true | disease = true)
p0 = P(finding = true | disease = false)
````

When a finding is observed as present:

```text
LR+ = p1 / p0
```

When a finding is observed as absent:

```text
LR- = (1 - p1) / (1 - p0)
```

The posterior is then updated independently for each disease node:

```text
posterior odds = prior odds × product(LR for observed findings)
```

Disease posteriors are not normalized across disease nodes. Each disease is evaluated as an independent binary or multi-label posterior.

## Relationship to BayesSeed logistic parameters

Vestibular-BayesSeed used logistic coefficients:

```text
P(disease | findings) = sigmoid(intercept + Σ beta_i × finding_i)
```

In that framework, diagnostic evidence was mapped to log-odds coefficients, usually using:

```text
beta ≈ ln(LR)
```

Vestibular-GenBN does not store `beta` values. Instead, it stores the underlying generative likelihoods:

```text
P(finding | disease)
P(finding | not disease)
```

The log-likelihood contribution is computed during inference:

```text
log LR = ln(P(finding | disease) / P(finding | not disease))
```

Therefore, evidence should be entered as likelihood probabilities rather than as logistic coefficients.

## Base transformations

When sensitivity and specificity are available for a finding or test:

```text
LR+ = sensitivity / (1 - specificity)
LR- = (1 - sensitivity) / specificity
```

A likelihood row can then be initialized by setting:

```text
p1 = sensitivity
p0 = 1 - specificity
```

For example, if a test has sensitivity 0.82 and specificity 0.71:

```text
p1 = 0.82
p0 = 0.29
LR+ = 0.82 / 0.29 = 2.83
log LR+ = 1.04
```

If only LR+ and an estimated p1 are available:

```text
p0 = p1 / LR+
```

If only LR- and p1 are available:

```text
p0 = 1 - ((1 - p1) / LR-)
```

All probabilities should remain within a plausible range and should usually avoid exact 0 or 1.

## Conservative initialization rule

The recommended initialization rule is:

```text
Use literature values when available.
Discount values when evidence is indirect, heterogeneous, or not pathway-specific.
Avoid extreme p1/p0 separation in seed modules.
Explore uncertainty with sensitivity analysis.
```

A practical seed rule is:

```text
p1_seed = shrink(p1_literature toward 0.5)
p0_seed = shrink(p0_literature toward 0.5)
```

The degree of shrinkage depends on evidence quality, transportability, and whether the finding is encoded at the correct network layer.

## Qualitative likelihood scale

When no stable quantitative estimate is available, use conservative qualitative seed values.

| Evidence strength      | Suggested p1 | Suggested p0 | Approximate LR+ | Interpretation                                    |
| ---------------------- | -----------: | -----------: | --------------: | ------------------------------------------------- |
| Very weak supportive   |    0.55–0.65 |    0.35–0.45 |         1.2–1.9 | Nonspecific symptom or weak contextual support    |
| Weak supportive        |    0.60–0.70 |    0.25–0.40 |         1.5–2.8 | Soft phenotype component                          |
| Moderate supportive    |    0.70–0.85 |    0.10–0.30 |         2.3–8.5 | Useful syndrome-level or test-level support       |
| Strong supportive      |    0.80–0.95 |    0.03–0.15 |        5.3–31.7 | Criteria-defining or highly compatible pattern    |
| Very strong supportive |    0.90–0.98 |    0.01–0.05 |           18–98 | Highly specific objective pattern; use cautiously |

For competing or atypical findings, reverse the relationship:

```text
p1 < p0
```

For example, a central red flag finding for a peripheral vestibular disease may have:

```text
p1 = 0.05
p0 = 0.30
LR+ = 0.17
```

This decreases the posterior probability of that peripheral disease when the finding is present.

## Evidence-quality categories

Recommended categories:

| Evidence quality           | Meaning                                                                          |
| -------------------------- | -------------------------------------------------------------------------------- |
| `guideline_informed_seed`  | Based on official diagnostic criteria, consensus documents, or major guidelines  |
| `literature_informed_seed` | Based on published diagnostic studies, reviews, or cohort data                   |
| `expert_seed`              | Based on expert clinical reasoning when stable quantitative data are unavailable |
| `placeholder_seed`         | Temporary value requiring later evidence review                                  |

The `evidence_quality` field should not imply clinical validation. It describes the origin and maturity of the seed parameter.

## Placement discount

The same clinical observation should not be reused repeatedly as independent evidence. Placement is therefore critical.

| Placement                            | Recommendation                                                          |
| ------------------------------------ | ----------------------------------------------------------------------- |
| Raw observation → finding pattern    | Use deterministic or rule-based mapping when possible                   |
| Finding pattern → disease likelihood | Encode the diagnostic likelihood here                                   |
| Multiple correlated raw observations | Aggregate into a phenotype-support node before posterior updating       |
| Criteria audit output                | Do not use as posterior evidence                                        |
| Safety/action flag                   | Do not use as posterior evidence unless explicitly modeled as a finding |

In GenBN, strict diagnostic criteria and action rules should remain separate audit outputs. They should not be used as likelihood evidence for disease posterior updating.

## Exclusive graded support groups

Some correlated findings are grouped into mutually exclusive graded phenotype-support levels, such as:

```text
weak support
moderate support
strong support
```

Only the active support level should contribute likelihood evidence.

Inactive levels in the same exclusive group are structural outputs of the grading cascade, not true negative observations. Therefore, inactive levels should not be interpreted as negative evidence.

Example:

```text
pc_bppv_positional_phenotype_support_strong = yes
pc_bppv_positional_phenotype_support_moderate = no
pc_bppv_positional_phenotype_support_weak = no
```

Only the strong support node should contribute a likelihood ratio.

## Priors

Disease priors should not be interpreted as general population prevalence.

They should represent the expected probability of a disease in the intended diagnostic setting, such as:

* first-visit otology dizziness clinic;
* tertiary vestibular referral clinic;
* emergency department acute vestibular syndrome pathway;
* history-only triage stage;
* bedside-examination stage;
* laboratory-confirmed stage.

The default seed prior in the current demonstration bundle is a research placeholder and should be reconfigured before external validation.

## Implementation fields

Recommended likelihood row fields:

```json
{
  "disease_node": "dx_pc_bppv",
  "finding_node": "pc_bppv_positional_phenotype_support_strong",
  "time_slice": "bedside_exam",
  "p_finding_true_given_disease_true": 0.90,
  "p_finding_true_given_disease_false": 0.03,
  "evidence_quality": "guideline_informed_seed",
  "use": "use_directly",
  "notes": "Strong canal-specific positional phenotype support for posterior-canal BPPV."
}
```

Optional future fields may include:

```json
{
  "p1_range": [0.80, 0.95],
  "p0_range": [0.01, 0.06],
  "evidence_basis": "Guideline-informed seed value",
  "source_type": "diagnostic_criteria",
  "applicability_concerns": "May vary by examiner expertise and case mix"
}
```

## Worked example

Suppose a canal-specific positional finding is strongly associated with posterior-canal BPPV, but published diagnostic accuracy estimates are heterogeneous.

A conservative seed row may be:

```json
{
  "disease_node": "dx_pc_bppv",
  "finding_node": "pc_bppv_positional_phenotype_support_strong",
  "time_slice": "bedside_exam",
  "p_finding_true_given_disease_true": 0.90,
  "p_finding_true_given_disease_false": 0.03,
  "evidence_quality": "guideline_informed_seed",
  "use": "use_directly",
  "notes": "Strong canal-specific positional phenotype support."
}
```

If the finding is present:

```text
LR+ = 0.90 / 0.03 = 30
```

If the finding is absent:

```text
LR- = (1 - 0.90) / (1 - 0.03) = 0.10 / 0.97 = 0.10
```

However, if this node belongs to an exclusive graded support group, inactive lower-grade levels should not be counted as negative evidence.

## Sensitivity analysis

All seed likelihoods should be treated as uncertain.

Recommended sensitivity ranges:

| Evidence strength |   Suggested p1 range |   Suggested p0 range |
| ----------------- | -------------------: | -------------------: |
| Weak              |           ±0.10–0.20 |           ±0.05–0.15 |
| Moderate          |           ±0.05–0.15 |           ±0.03–0.10 |
| Strong            |           ±0.03–0.10 |           ±0.01–0.05 |
| Expert-only       | broad range required | broad range required |

Sensitivity analysis should examine whether disease ranking, posterior magnitude, or action flags are robust to plausible parameter changes.

## Practical warnings

Do not treat literature-derived diagnostic accuracy estimates as universally transportable. Case mix, referral setting, disease spectrum, test protocol, examiner expertise, and diagnostic reference standards can substantially change `P(finding | disease)` and `P(finding | not disease)`.

Seed likelihood values are intended to make the knowledge bundle transparent, executable, and testable. They are not a substitute for local calibration or prospective clinical validation.
