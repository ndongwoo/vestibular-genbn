# Vestibular-GenBN

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20470541.svg)](https://doi.org/10.5281/zenodo.20470541)
[![tests](https://github.com/ndongwoo/vestibular-genbn/actions/workflows/tests.yml/badge.svg)](https://github.com/ndongwoo/vestibular-genbn/actions/workflows/tests.yml)

**Vestibular-GenBN** is an open-source Python seed framework for modular generative Bayesian
diagnostic networks in vestibular medicine.

The project is designed for research, education, and transparent clinical knowledge engineering.
It is **not** a validated clinical decision-support system, not a medical device, and must not be
used for diagnosis, treatment, triage, or patient management without appropriate clinical
validation, governance, and regulatory review.

## Core modeling policy

- Disease posteriors are computed independently as binary one-vs-rest or multi-label posteriors.
- Posterior probabilities are **not** normalized to sum to 1 across diseases.
- Candidate sets define which disease nodes are evaluated in a run.
- BPPV and Ménière-spectrum disorders are included as active base examples.
- Additional vestibular disorders are included as placeholders for future activation.
- The framework supports mutually exclusive graded phenotype support groups for representing correlated observations.

## Architecture overview

Vestibular-GenBN separates probabilistic phenotype support from deterministic criteria audit. In the current implementation, the BPPV module implements mutually exclusive weak, moderate, and strong phenotype-support groups for both posterior-canal and horizontal-canal BPPV. These graded support nodes are used as posterior evidence for dx_pc_bppv and dx_hc_bppv, while strict criteria and action flags remain separate audit outputs. Ménière-spectrum disorders currently retain the existing pattern-node evidence structure.

## Repository layout

```text
knowledge/default_v0_1/   JSON knowledge bundle
src/vestibular_genbn/     Reusable Python package
examples/                 Synthetic cases and runnable example script
tests/                    Pytest-based validation and execution tests
docs/                     User and developer documentation
app/                      Optional Streamlit demonstration app
paper/                    SoftwareX manuscript-supporting material
```

## Installation

```bash
pip install -e ".[dev]"
```

For the optional Streamlit app:

```bash
pip install -e ".[app,dev]"
```

## Quick start

Validate the default knowledge bundle:

```bash
vestibular-genbn validate knowledge/default_v0_1
```

Run synthetic cases:

```bash
vestibular-genbn run \
  --case-file examples/synthetic_cases.csv \
  --knowledge knowledge/default_v0_1 \
  --output examples/output_core_v0_1.csv
```

Run the example script:

```bash
python examples/run_examples.py
```

Run tests:

```bash
pytest
```

Optional Streamlit demo:

```bash
streamlit run app/streamlit_app.py
```

## Medical disclaimer

The included parameters are transparent seed values for software demonstration and future
calibration. They are not validated diagnostic probabilities.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history.