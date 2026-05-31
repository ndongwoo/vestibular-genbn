# Sensitivity analysis

Vestibular-GenBN includes a small one-way sensitivity-analysis utility for inspecting how selected seed likelihood parameters affect disease-specific posterior probabilities.

The current implementation varies:

```text
p1 = P(finding = true | disease = true)
````

while holding the corresponding seed value of:

```text
p0 = P(finding = true | disease = false)
```

fixed. This is intended as a transparent software demonstration and parameter-auditing tool. It is not a clinical calibration procedure.

## Why sensitivity analysis is needed

The default knowledge bundle contains conservative seed likelihoods derived from guideline-informed, literature-informed, and expert-informed sources. These parameters are intentionally editable. Their purpose is to make the knowledge representation executable and inspectable, not to claim external clinical calibration.

Sensitivity analysis helps answer questions such as:

* Does the top posterior remain stable if a seed likelihood is changed within a plausible range?
* Which finding-to-disease likelihoods have large effects on synthetic demonstration cases?
* Which parameters should receive priority during future evidence review or local calibration?

## Configuration file

The default ranges are stored in:

```text
knowledge/default_v0_1/config/sensitivity_ranges.json
```

Each entry describes one disease-finding likelihood parameter:

```json
{
  "id": "pc_bppv_moderate_support_p1",
  "disease_node": "dx_pc_bppv",
  "finding_node": "pc_bppv_positional_phenotype_support_moderate",
  "parameter": "p_finding_true_given_disease_true",
  "default": 0.80,
  "p0_fixed_at": 0.04,
  "p1_values": [0.70, 0.80, 0.90],
  "evidence_quality": "guideline_informed_seed",
  "recommended_case_ids": ["S01_typical_pc_bppv"],
  "rationale": "Moderate posterior-canal BPPV phenotype support is a canal-specific bedside pattern, but the seed value should remain editable and sensitivity-tested."
}
```

The fields have the following meaning:

| Field                  | Meaning                                                      |
| ---------------------- | ------------------------------------------------------------ |
| `id`                   | Stable identifier for the sensitivity setting                |
| `disease_node`         | Target disease posterior to inspect                          |
| `finding_node`         | Likelihood row to vary                                       |
| `parameter`            | Currently `p_finding_true_given_disease_true`                |
| `default`              | Seed p1 value in the likelihood table                        |
| `p0_fixed_at`          | Seed p0 value held fixed during current one-way analysis     |
| `p1_values`            | Values to evaluate for p1                                    |
| `evidence_quality`     | Evidence-maturity label from the likelihood table            |
| `recommended_case_ids` | Synthetic cases where the finding is expected to be relevant |
| `rationale`            | Reason for including the parameter and range                 |

## API example

```python
from pathlib import Path
import json

from vestibular_genbn import load_knowledge_bundle
from vestibular_genbn.inference import load_case_csv
from vestibular_genbn.sensitivity import one_way_likelihood_sensitivity

repo = Path(".")
bundle = load_knowledge_bundle(repo / "knowledge" / "default_v0_1")
cases = load_case_csv(repo / "examples" / "synthetic_cases.csv")
case = next(row for row in cases if row["case_id"] == "S01_typical_pc_bppv")

config = json.loads(
    (repo / "knowledge" / "default_v0_1" / "config" / "sensitivity_ranges.json")
    .read_text(encoding="utf-8")
)
setting = next(
    item for item in config["parameters"]
    if item["id"] == "pc_bppv_moderate_support_p1"
)

rows = one_way_likelihood_sensitivity(
    bundle,
    case,
    disease_node=setting["disease_node"],
    finding_node=setting["finding_node"],
    p1_values=setting["p1_values"],
)

for row in rows:
    print(row)
```

Example output:

```text
{'disease_node': 'dx_pc_bppv', 'finding_node': 'pc_bppv_positional_phenotype_support_moderate', 'p1': 0.7, 'posterior': 0.8985597996242956}
{'disease_node': 'dx_pc_bppv', 'finding_node': 'pc_bppv_positional_phenotype_support_moderate', 'p1': 0.8, 'posterior': 0.9100998890122086}
{'disease_node': 'dx_pc_bppv', 'finding_node': 'pc_bppv_positional_phenotype_support_moderate', 'p1': 0.9, 'posterior': 0.9192825112107623}
```

## Interpretation

For a finding observed as present, increasing `p1` generally increases the likelihood ratio:

```text
LR+ = p1 / p0
```

and therefore increases the posterior odds for the target disease, all else being equal.

For a finding observed as absent, the relevant likelihood ratio is:

```text
LR- = (1 - p1) / (1 - p0)
```

The current configuration focuses on demonstration cases where the selected finding is present, because these examples are easiest to interpret and test.

## Relationship to exclusive graded support groups

BPPV phenotype-support nodes may be arranged as mutually exclusive graded support levels, such as weak, moderate, and strong support. Inactive levels in these groups are structural outputs of the grading cascade and are not treated as negative evidence. Therefore, sensitivity analysis should usually vary the active support level for the relevant synthetic case.

For example, in `S01_typical_pc_bppv`, the moderate posterior-canal support level contributes to `dx_pc_bppv`, so `pc_bppv_positional_phenotype_support_moderate` is an appropriate sensitivity target for that case.

## Limitations

The current implementation is intentionally minimal:

* it varies p1 only;
* it holds p0 fixed;
* it evaluates one parameter at a time;
* it reports the target disease posterior, not a full tornado plot or probabilistic uncertainty interval;
* it does not recalibrate parameters from patient-level data.

Future extensions may add p0 sensitivity, two-way sensitivity analysis, prior sensitivity, plotting utilities, and batch export of sensitivity tables.

## Clinical-use warning

Sensitivity ranges in the default bundle are seed ranges for software inspection. They should not be interpreted as validated clinical uncertainty intervals. Case mix, referral setting, examiner expertise, test protocol, and diagnostic reference standards can substantially change likelihood parameters.
