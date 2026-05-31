# Changelog for Vestibular-GenBN v0.1.4

## Summary

Vestibular-GenBN v0.1.4 is a SoftwareX submission-preparation release focused on reproducibility, inspectability, and reviewer-facing documentation. This version preserves the core generative Bayesian inference design while adding detailed JSON output, sensitivity-analysis configuration, improved example generation, enhanced Streamlit inspection views, and an updated manuscript package.

The release continues to evaluate candidate disease nodes as independent one-vs-rest posteriors rather than as a mutually exclusive closed diagnostic set.

## Key Changes

### 1. Version Updates

- Updated the project version to `0.1.4`.
- Updated package metadata and release-facing documentation to reflect v0.1.4.
- Updated the SoftwareX manuscript draft to describe the v0.1.4 feature set.

Files commonly affected:

- `pyproject.toml`
- `src/vestibular_genbn/__init__.py`
- `CITATION.cff`
- `README.md`
- `paper/manuscript.md`
- `knowledge/default_v0_1/project_manifest.json`
- `knowledge/default_v0_1/README.md`

### 2. Detailed JSON Output

Added detailed case-level JSON output for reproducible inspection of inference results.

The detailed JSON output exposes:

- raw case inputs;
- evaluated finding-pattern values;
- independent disease posteriors;
- prior and posterior values for each disease node;
- likelihood-ratio contributions;
- log-likelihood-ratio contributions;
- `P(finding | disease)` and `P(finding | not disease)` values;
- criteria-audit and action-flag outputs.

This makes the inference pathway more transparent and allows reviewers to inspect how each posterior was generated.

Main files:

- `src/vestibular_genbn/inference.py`
- `src/vestibular_genbn/cli.py`
- `examples/run_examples.py`
- `tests/test_cli.py`

Generated example output:

- `examples/output_core_v0_1_detailed.json`
- `examples/output_core_v0_1.csv`

### 3. Example-Generation Workflow

Updated the example runner so that synthetic cases can generate both:

- a summary CSV output; and
- a detailed JSON output with case-level inference details.

The example-generation script is intended to support reproducible SoftwareX review and archived-release inspection.

Main file:

- `examples/run_examples.py`

Example command:

```bash
python examples/run_examples.py
````

Expected outputs:

```text
examples/output_core_v0_1.csv
examples/output_core_v0_1_detailed.json
```

### 4. Sensitivity-Analysis Configuration

Added seed sensitivity-analysis configuration for selected likelihood parameters in the default knowledge bundle.

The current sensitivity-analysis implementation focuses on one-way variation of:

```text
p1 = P(finding = true | disease = true)
```

while holding:

```text
p0 = P(finding = true | disease = false)
```

fixed at the seed value.

New configuration file:

* `knowledge/default_v0_1/config/sensitivity_ranges.json`

New or updated documentation:

* `docs/sensitivity_analysis.md`

New or updated tests:

* `tests/test_sensitivity.py`

The sensitivity configuration is intended for software inspection and parameter-auditing. It is not intended to represent validated clinical uncertainty intervals.

### 5. Evidence-to-Likelihood Documentation

Added documentation describing how diagnostic evidence should be represented as generative likelihood parameters.

The documentation distinguishes the GenBN likelihood approach from earlier prediction-oriented logistic coefficient approaches.

Main concepts documented:

* `P(finding | disease)`
* `P(finding | not disease)`
* positive and negative likelihood ratios;
* qualitative seed likelihood scales;
* evidence-quality categories;
* placement of raw observations, derived findings, audit outputs, and action flags;
* exclusive graded support groups;
* sensitivity-analysis considerations.

New documentation:

* `docs/evidence_to_likelihood_mapping.md`

### 6. Streamlit Demonstration Interface Enhancement

Enhanced the optional Streamlit demonstration interface to support interactive inspection of the knowledge bundle and inference outputs.

The updated interface includes:

* case-level simulation;
* independent disease-posterior display;
* likelihood-ratio contribution inspection;
* evaluated finding-pattern display;
* audit/action flag display;
* knowledge-bundle viewer;
* likelihood/evidence metadata table;
* sensitivity-analysis panel;
* Mermaid network export.

Main file:

* `app/streamlit_app.py`

Example command:

```bash
streamlit run app/streamlit_app.py
```

### 7. SoftwareX Manuscript Update

Updated the SoftwareX manuscript to reflect v0.1.4.

Main changes include:

* updated version references to v0.1.4;
* description of detailed JSON output;
* description of one-way likelihood sensitivity analysis;
* description of the enhanced Streamlit demonstration interface;
* addition of Figure 3 for the optional Streamlit interface;
* updated SoftwareX metadata table;
* updated Code availability and Zenodo release citation placeholders.

Main file:

* `paper/manuscript.md`

Important release note:

* The Zenodo DOI should be updated after the final v0.1.4 GitHub release is archived.

### 8. Documentation and Reviewer-Facing Improvements

Improved documentation for reproducible review and software inspection.

Documentation now better covers:

* software architecture;
* default knowledge-bundle structure;
* evidence-to-likelihood mapping;
* sensitivity analysis;
* command-line execution;
* example-output generation;
* optional Streamlit demonstration.

Relevant files may include:

* `README.md`
* `docs/overview.md`
* `docs/softwarex_user_guide.md`
* `docs/cli_reference.md`
* `docs/sensitivity_analysis.md`
* `docs/evidence_to_likelihood_mapping.md`

### 9. Formatting and Quality Control

The v0.1.4 preparation process includes formatting and quality checks using:

* `black`
* `ruff`
* `mypy`
* `pytest`

Recommended verification commands:

```bash
black .
ruff check .
mypy src/vestibular_genbn
pytest
python examples/run_examples.py
```

Optional package-build verification:

```bash
python -m build
pip install dist/vestibular_genbn-0.1.4-py3-none-any.whl
vestibular-genbn --version
vestibular-genbn validate knowledge/default_v0_1
```

## Files Changed

Expected major changed or newly added files include:

```text
pyproject.toml
README.md
CITATION.cff
DEVELOPMENT.md
paper/manuscript.md
app/streamlit_app.py
examples/run_examples.py
examples/output_core_v0_1.csv
examples/output_core_v0_1_detailed.json
src/vestibular_genbn/__init__.py
src/vestibular_genbn/cli.py
src/vestibular_genbn/inference.py
src/vestibular_genbn/sensitivity.py
tests/test_cli.py
tests/test_sensitivity.py
docs/evidence_to_likelihood_mapping.md
docs/sensitivity_analysis.md
knowledge/default_v0_1/README.md
knowledge/default_v0_1/project_manifest.json
knowledge/default_v0_1/config/sensitivity_ranges.json
```

## Notes on Knowledge-Bundle Versioning

The software release version is updated to `0.1.4`.

However, the default knowledge-bundle directory remains:

```text
knowledge/default_v0_1
```

This directory name indicates the default v0.1 knowledge-bundle family and should not necessarily be renamed for every software patch release.

Similarly, schema or component-level fields such as:

```text
schema_version
inference_policy_v0_1
candidate_set_core_v0_1
```

may remain unchanged unless the underlying schema or knowledge-bundle contract changes.

## Release Checklist

Before tagging the final v0.1.4 release:

```bash
black .
ruff check .
mypy src/vestibular_genbn
pytest
python examples/run_examples.py
vestibular-genbn --version
vestibular-genbn validate knowledge/default_v0_1
```

Check for stale release-version references:

```bash
rg -n "v0\.1\.[0-3]|Version 0\.1\.[0-3]|0\.1\.[0-3]" \
  --glob '!*.egg-info/**' \
  --glob '!dist/**' \
  --glob '!build/**' \
  .
```

Do not automatically replace all `0.1.0` or `v0_1` strings. Some of these refer to schema, bundle-family, or configuration names rather than the software release version.

## Zenodo and Citation Notes

After creating the GitHub v0.1.4 release, archive it on Zenodo and update the following files with the final v0.1.4 DOI:

```text
README.md
CITATION.cff
paper/manuscript.md
```

The recommended software citation format is:

```text
Nam DW. Vestibular-GenBN: A modular generative Bayesian network framework for vestibular diagnostic knowledge engineering. Version 0.1.4 [software]. Zenodo; 2026. doi:10.5281/zenodo.20470541.
```

## Clinical-Use Warning

Vestibular-GenBN v0.1.4 remains research software for diagnostic knowledge engineering, education, and reproducible demonstration.

The default knowledge bundle uses synthetic cases and seed likelihood parameters. It is not externally validated, calibrated for clinical deployment, or intended for unvalidated clinical decision-making.

