# Vestibular-GenBN: An open-source framework for modular generative Bayesian networks in vestibular diagnostic knowledge engineering

**Dong Woo Nam***a,b,c, **Ja-Won Koo**b

a Department of Otorhinolaryngology-Head and Neck Surgery, Graduate School of Medicine, Chungbuk National University, Cheongju, Republic of Korea
b Department of Otorhinolaryngology-Head and Neck Surgery, Seoul National University Bundang Hospital, Seongnam, Republic of Korea
c Department of Otorhinolaryngology-Head and Neck Surgery, SMG-SNU Boramae Medical Center, Seoul, Republic of Korea

\* Corresponding author.
E-mail address: [ndongwoo@gmail.com](mailto:ndongwoo@gmail.com) (D.W. Nam).

------

## Abstract

Vestibular-GenBN is an open-source Python framework for constructing modular generative Bayesian networks for vestibular diagnostic knowledge engineering. The software separates disease-specific clinical knowledge from reusable inference code by representing disease nodes, observations, derived finding patterns, likelihood parameters, criteria-audit rules, and action overlays in JSON knowledge bundles. Unlike prediction-oriented diagnostic models, the framework uses a disease-to-finding structure and updates each candidate disease node independently as a one-vs-rest posterior, allowing overlapping or comorbid vestibular disorders to be represented without forcing probabilities to sum to one. The package provides knowledge-bundle validation, derived-node evaluation, posterior-odds inference, batch execution, visualization, sensitivity analysis, unit tests, a command-line interface, and an optional Streamlit demonstration interface. Version 0.1.3 includes worked examples for benign paroxysmal positional vertigo and Ménière-spectrum disorders. Vestibular-GenBN is intended for research, education, and reproducible clinical knowledge engineering, not for unvalidated clinical decision-making.

## Keywords 

Bayesian network; Vestibular disorders; Dizziness; Clinical decision support

## Metadata 

| **Nr** | **Code  metadata description**                               | **Metadata**                                                 |
| ------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| C1     | Current code version                                         | v0.1.3                                                       |
| C2     | Permanent link to  code/repository used for this code version | https://github.com/ndongwoo/vestibular-genbn; archived version: https://doi.org/10.5281/zenodo.20460819 |
| C3     | Legal code license                                           | Apache License 2.0                                           |
| C4     | Code versioning system used                                  | git                                                          |
| C5     | Software code languages,  tools and services used            | Python 3.10+, JSON, YAML;  NumPy, pandas, Pydantic, jsonschema, NetworkX, matplotlib, Click, Rich,  PyYAML; optional Streamlit and Plotly; pytest, pytest-cov, ruff, black, mypy,  and Jupyter for development/testing; GitHub and Zenodo for version control  and archival release |
| C6     | Compilation requirements,  operating environments and dependencies | Python >=3.10. Runtime  dependencies: numpy>=1.24, pandas>=2.0, pydantic>=2.5,  jsonschema>=4.19, networkx>=3.1, matplotlib>=3.7, click>=8.1,  rich>=13.0, pyyaml>=6.0. Optional app dependencies: streamlit>=1.32  and plotly>=5.18. Development dependencies: pytest>=7.0, pytest-cov,  ruff, black, mypy, and jupyter. |
| C7     | If available, link to  developer documentation/manual        | https://github.com/ndongwoo/vestibular-genbn/tree/main/docs  |
| C8     | Support email for questions                                  | ndongwoo@gmail.com                                           |

 

## 1. Motivation and significance

Dizziness and vertigo diagnosis requires integration of heterogeneous clinical evidence, including symptom timing and triggers, positional nystagmus, audiometry, vestibular laboratory tests, imaging findings, neurological red flags, and longitudinal clinical context [1]. Consensus diagnostic criteria are clinically useful, but they can be difficult to operationalize when information is incomplete, when test results are unavailable at an early visit, or when overlapping syndromes coexist. Purely data-driven diagnostic models may also be difficult to train in low-data clinical domains and may not clearly disclose how disease-specific assumptions, formal diagnostic criteria, and literature-derived evidence are being used.

Bayesian network modeling provides a transparent framework for representing uncertainty, missing observations, conditional dependencies, and diagnostic overlap [2, 3]. In many diagnostic applications, however, models are built in a prediction-oriented direction, with symptoms and test results pointing directly toward diagnosis nodes. This structure is intuitive for classification, but it can blur the distinction between disease states, observable manifestations, engineered diagnostic features, and deterministic criteria fulfillment. It may also make it difficult to incorporate disease-specific finding distributions, likelihood ratios, sensitivity/specificity estimates, false-negative test behavior, and uncertainty in the availability of clinical observations.

Vestibular-GenBN was developed to provide a reusable seed framework for generative diagnostic Bayesian networks in vestibular medicine. In this design, disease nodes generate symptoms, bedside findings, audiovestibular test results, imaging findings, exclusion features, and derived clinical observations. Inference proceeds in the reverse direction: observed findings are used to update the probability of each disease node. This disease-to-finding structure is intended to support transparent literature-based parameterization, modular disease expansion, explicit handling of missing evidence, and separation between probabilistic inference and deterministic criteria audit.

The initial software release is research infrastructure rather than a validated clinical decision-support system. It demonstrates how vestibular disease knowledge can be encoded in JSON files, validated, executed, visualized, tested, and subjected to sensitivity analysis using common inference code. The first active worked modules focus on representative vestibular disorders with different diagnostic structures: benign paroxysmal positional vertigo (BPPV), a positional/nystagmus-driven disorder, and Ménière-spectrum disorders, which involve episodic audio-vestibular and audiometric evidence. Additional vestibular disorders are represented through the same extensible registry-based design and can be activated in future versions without rewriting the core inference engine.
 

## 2. Software description

## 2.1 Software architecture

Vestibular-GenBN separates disease-specific clinical knowledge from reusable inference logic. Clinical knowledge is stored as a modular JSON knowledge bundle, whereas the Python package handles bundle loading, internal-reference validation, derived-node evaluation, posterior-odds inference, batch execution, audit/action overlays, network visualization, and sensitivity analysis. The same knowledge bundle can be used through the Python API, command-line interface, tests, batch examples, documentation, and an optional Streamlit demonstration interface.

The core workflow is as follows: (i) load a JSON knowledge bundle; (ii) validate disease-node, observation-node, finding-node, likelihood-row, and audit-rule references; (iii) accept a synthetic or user-defined case as raw observation values; (iv) evaluate deterministic derived finding patterns from raw observations; (v) update each disease node independently using observed evidence; and (vi) return one-vs-rest disease posteriors, ranked outputs, evidence-contribution summaries, criteria-audit results, safety/action overlays, network exports, and sensitivity-analysis results. The overall architecture and information flow are summarized in Figure 1.

The framework treats candidate diseases as disease nodes to be evaluated, not as a closed mutually exclusive diagnostic universe. Accordingly, disease probabilities are computed as independent binary or multi-label posteriors and are not constrained to sum to one across candidate diagnoses. This behavior is important in vestibular medicine because overlapping syndromes, comorbid disorders, and partially observed presentations are common.

The framework supports a graded supportive phenotype layer for representing correlated observations. In the current release, the BPPV module implements this mechanism for both posterior-canal and horizontal-canal BPPV by aggregating canal-specific positional findings into mutually exclusive weak, moderate, and strong phenotype-support nodes. These graded support nodes serve as posterior evidence for `dx_pc_bppv` and `dx_hc_bppv`, respectively, reducing inappropriate double counting of correlated positional findings while preserving the generative disease-to-phenotype interpretation. Ménière-spectrum disorders currently retain the existing pattern-node evidence structure. Formal diagnostic criteria are implemented separately as deterministic audit outputs and are not used as posterior likelihood evidence.

## 2.2 Node taxonomy and modeling pattern

The framework uses five main registries: disease nodes, raw observation nodes, derived finding-pattern nodes, likelihood rows, and audit/action outputs. Disease nodes represent candidate disorders; raw observations represent case-level inputs such as symptoms, examination findings, audiometry, vestibular tests, imaging findings, and red flags; derived nodes aggregate clinically related observations into interpretable finding patterns; likelihood rows encode disease-specific finding distributions as P(finding | disease) and P(finding | not disease); and audit/action outputs provide criteria support labels, safety alerts, or workflow recommendations without overriding posterior inference.

The preferred modeling pattern places disease nodes upstream of clinical findings. Raw observations may activate derived finding patterns, and these patterns are then used as evidence for one-vs-rest posterior updating. Deterministic criteria fulfillment is handled separately as an audit layer rather than being treated as synonymous with the latent disease node. This separation allows the same framework to preserve probabilistic inference, criteria-based interpretation, and safety/action recommendations as distinct outputs. An example of this generative network structure is visualized in Figure 2.

**Figure 2**. Example network visualization. Disease nodes generate observable symptoms, bedside findings, audiometric findings, vestibular test results, and derived clinical features. Inference uses observed evidence to update one-vs-rest disease probabilities.

## 2.3 Generative diagnostic inference

In a generative diagnostic network, each disease node defines the expected distribution of findings under that disease. For a disease node D and a set of observed findings F={f_1, …, F_k}, inference can be expressed conceptually as:

P(D | F) ∝ P(D) × P(F | D).

For executable one-vs-rest inference, Vestibular-GenBN uses a posterior-odds update:

odds(D | F) = odds(D) × ∏ LR_i

where each likelihood ratio compares the probability of the observed finding state under the disease with the probability of that finding state under the complement of the disease [4].

Observed yes values contribute positive-evidence likelihood ratios, observed no values contribute negative-evidence likelihood ratios, and unknown values are omitted from the likelihood product by default [1]. This policy prevents unperformed tests, unavailable audiometry, missing imaging, or undocumented symptoms from being incorrectly treated as absent.

Clinical findings are often correlated. Vestibular-GenBN therefore supports derived finding patterns and structured module design to reduce inappropriate double counting. Strongly related raw observations can be grouped into clinically interpretable derived constructs before contributing to disease-level inference. The software also supports evidence annotations and sensitivity-analysis ranges, allowing uncertain parameters to be inspected and varied.

Prior probabilities are supplied separately from disease-specific finding distributions. This allows future use of age-, sex-, referral-setting-, or population-specific priors without hard-coding those priors into disease modules. When external prior tables are unavailable, the framework can use neutral or conservative priors for demonstration purposes. Such outputs should be interpreted as model-behavior examples rather than calibrated clinical probabilities.

## 2.4 Derived nodes, criteria audit, and action overlays

Derived nodes transform raw clinical observations into auditable clinical constructs. Examples include positional nystagmus patterns, episodic audio-vestibular patterns, cochlear audiometric patterns, central red-flag patterns, and retrocochlear concern patterns. Derived nodes are deterministic in the initial seed implementation, although the architecture allows future probabilistic extensions.

The framework allows diagnostic criteria to inform the design of derived features, but it does not require deterministic criteria fulfillment to be treated as the final diagnosis. Formal criteria often combine symptom timing, test findings, certainty levels, and exclusion rules. Encoding all criteria directly as diagnostic outputs can make a model brittle when evidence is missing. By contrast, Vestibular-GenBN can represent criteria-relevant features as findings generated by disease states, use them probabilistically during inference, and then apply criteria support rules as an audit layer.

Safety and action overlays are also separated from posterior inference. Central red-flag patterns, retrocochlear concern patterns, and workflow recommendations such as urgent central evaluation or MRI IAC/CPA consideration are computed as interpretive outputs. They do not overwrite independent disease posterior probabilities.

## 2.5 Software functionalities

Vestibular-GenBN supports the complete workflow required to define, validate, execute, and inspect modular generative Bayesian diagnostic networks. It loads vestibular knowledge bundles encoded in JSON files and validates required fields, node references, likelihood definitions, evidence annotations, and module consistency. Given raw clinical input values, the software evaluates derived clinical constructs and applies generative posterior-odds inference to estimate disease-specific posterior probabilities.

For reproducible demonstrations, the package can execute synthetic or user-supplied case files in batch mode. It provides one-way sensitivity analysis for selected parameters, exports network structures for visualization, and reports evidence contributions by disease node. The package is accessible through a Python API, a command-line interface, synthetic examples, unit tests, documentation, and an optional Streamlit demonstration interface.

## 2.6 Interfaces and sample usage

The package can be used programmatically or from the command line.

```bash
# Validate the default knowledge bundle
vestibular-genbn validate knowledge/default_v0_1
# Run synthetic cases
vestibular-genbn run --case-file examples/synthetic_cases.csv --knowledge knowledge/default_v0_1 --output examples/output_core_v0_1.csv
```

Full installation instructions, Python API examples, test commands, and the optional Streamlit demonstration are provided in the repository documentation.
 

## 3. Illustrative examples

The initial release includes seven synthetic demonstration cases designed to show model behavior, derived-node activation, missing-evidence handling, safety/action overlays, and independent one-vs-rest posterior updating. These cases are not intended to estimate diagnostic accuracy, discrimination, calibration, or clinical utility. They provide reproducible examples for software testing and for illustrating how the active BPPV and Ménière-spectrum modules respond to different evidence patterns.

The demonstration cases include typical posterior-canal BPPV, typical horizontal-canal BPPV with geotropic nystagmus, subjective or possible BPPV, a central positional red-flag pattern, definite-like Ménière disease, probable or early Ménière-spectrum disease, and retrocochlear/asymmetric SNHL concern. Other vestibular disorders are represented as placeholder disease nodes for future module development and are not treated as calibrated worked examples in version 0.1.3. The execution results and main behaviors of these synthetic cases are summarized in Table 1.

 

| **Case** | **Expected  pattern**                          | **Top-ranked  disease node**       | **Grouped  interpretation**    | **Posterior** | **Main behavior**                                            |
| -------- | ---------------------------------------------- | ---------------------------------- | ------------------------------ | ------------- | ------------------------------------------------------------ |
| S01      | Typical  posterior-canal BPPV                  | dx_pc_bppv                         | BPPV spectrum                  | 0.910         | PC-BPPV node  dominant; canalith repositioning candidate flag positive |
| S02      | Typical  horizontal-canal BPPV, geotropic type | dx_hc_bppv                         | BPPV spectrum                  | 0.957         | HC-BPPV node  dominant; canalith repositioning candidate flag positive |
| S03      | Subjective or  possible BPPV                   | dx_subjective_or_possible_bppv     | BPPV spectrum                  | 0.651         | Subjective/possible  BPPV ranks highest; repositioning candidate flag positive |
| S04      | Central  positional red-flag pattern           | dx_central_positional_mimic        | Central  positional mimic      | 0.927         | Central  positional mimic dominates; urgent central-evaluation flag positive |
| S05      | Definite-like  Ménière disease pattern         | dx_meniere_disease                 | Ménière-spectrum               | 0.908         | Ménière disease  dominates with strong episodic, auditory, and audiometric evidence |
| S06      | Probable or early  Ménière-spectrum pattern    | dx_early_probable_meniere_spectrum | Ménière-spectrum               | 0.498         | Early/probable  Ménière-spectrum node exceeds definite MD    |
| S07      | Retrocochlear/asymmetric  SNHL concern         | dx_cpa_iac_retrocochlear_mimic     | Retrocochlear  mimic           | 0.546         | CPA/IAC retrocochlear  mimic ranks highest; MRI-consideration flag positive |

**Table 1**. Output from synthetic demonstration cases. The table summarizes the case identifier, intended pattern, top-ranked disease node or grouped interpretation, posterior probability, and principal behavior. Disease probabilities are computed as one-vs-rest posteriors and are not constrained to sum to one across candidate diseases. These examples demonstrate software behavior and are not intended to estimate clinical performance.

The BPPV examples demonstrate subtype-specific posterior updating for posterior-canal, horizontal-canal, subjective/possible BPPV, and central positional mimic patterns [5-7]. The Ménière-spectrum examples demonstrate how episodic vestibular symptoms, fluctuating auditory symptoms, and audiometric patterns can be encoded using the same registry–finding–likelihood structure [8, 9]. These examples are intended to demonstrate software behavior, not diagnostic accuracy or calibration.
Criteria-relevant features are represented as derived patterns and audit outputs rather than deterministic disease labels. This allows the software to report independent disease posteriors, criteria-support labels, and action flags separately. Future modules, such as vestibular migraine or functional dizziness, can be added by extending the observation registry, finding-pattern registry, likelihood table, and active candidate set without changing the inference engine.
 

## 4. Impact

Vestibular-GenBN provides reusable research software for constructing, inspecting, and executing modular generative Bayesian networks in a knowledge-rich but data-limited clinical domain. Its main contribution is not a validated diagnostic model, but an executable framework that makes disease-specific assumptions, evidence mappings, likelihood parameters, missingness rules, derived features, audit logic, and sensitivity ranges explicit and reproducible.

The framework addresses a common limitation of knowledge-engineered diagnostic models: clinical knowledge is often embedded directly in analysis scripts, making models difficult to inspect, revise, compare, or reuse. Vestibular-GenBN separates disease knowledge from inference code by storing disease nodes, observation registries, derived finding patterns, likelihood rows, criteria-audit rules, and action overlays in JSON knowledge bundles. This design allows investigators to update parameters, add disease modules, compare alternative assumptions, and examine the effect of missing evidence without rewriting the core software.

Although the default release focuses on vestibular disorders, the same registry–finding–likelihood–audit architecture could be adapted to other diagnostic domains in which evidence is incomplete, criteria-based, and partly literature-anchored. Before clinical deployment, disease-specific calibration, external validation, prospective evaluation, workflow testing, governance review, and regulatory assessment would be required. Its immediate value is therefore as an open and extensible platform for reproducible diagnostic knowledge engineering rather than as a clinical decision-making tool.


## 5. Conclusions

Vestibular-GenBN provides an open-source framework for constructing modular generative Bayesian networks for vestibular diagnostic knowledge engineering. The software separates disease-specific clinical knowledge from reusable inference logic, supports JSON-based knowledge bundles, evaluates derived clinical features, performs independent one-vs-rest disease posterior inference, and provides tools for batch execution, audit/action overlays, visualization, and sensitivity analysis. The initial worked examples demonstrate how representative vestibular disorders can be encoded in a transparent and extensible framework.
 

## Acknowledgments

This manuscript was adapted from the doctoral dissertation of Dong Woo Nam submitted to Chungbuk National University Graduate School in partial fulfillment of the requirements for the Doctor of Philosophy degree.

 

## Funding 

This work was supported by research grants from Seoul National University Bundang Hospital (Grant No. 06-2021-0482, 14-2022-0043, 02-2025-0039, and 13-2025-0008 to J.W. Koo). The funder had no role in study design, data collection, analysis, interpretation, or manuscript preparation.

 

## Data availability

No patient-level or clinical research dataset was used in this article. Synthetic cases are provided in the software repository. The demonstration cases are synthetic and are included in the archived software repository together with the source code.

 

## Code availability 

Source code is available at https://github.com/ndongwoo/vestibular-genbn. The archived version for this release is available through Zenodo [10].
 

## CRediT authorship contribution statement

Dong Woo Nam: Conceptualization, Methodology, Software, Validation, Visualization, Investigation, Writing – original draft, Writing – review & editing, Funding acquisition.

Ja-Won Koo: Conceptualization, Validation, Investigation, Writing – review & editing, Project administration, Funding acquisition.

 

## Declaration of generative AI and AI-assisted technologies in the manuscript preparation process

During the preparation of this work and the associated software, the authors used OpenCode with a locally served Qwen3.6:27B large language model to assist with code drafting, refactoring suggestions, debugging, and documentation consistency checks. The authors also used OpenAI ChatGPT to assist with manuscript proofreading, language editing, and consistency checking. After using this tool/service, the authors reviewed and edited the content as needed and takes full responsibility for the content of the published article.

 

## References

[1] Lin JH, Haug PJ. Exploiting missing clinical data in Bayesian network modeling for predicting medical problems. J Biomed Inform. 2008;41(1):1-14.
[2] Pearl J. Probabilistic Reasoning in Intelligent Systems: Networks of Plausible Inference. San Mateo, CA: Morgan Kaufmann; 1988.
[3] Polotskaya K, Muñoz-Valencia CS, Rabasa A, Quesada-Rico JA, Orozco-Beltrán D, Barber X. Bayesian Networks for the Diagnosis and Prognosis of Diseases: A Scoping Review. Machine Learning and Knowledge Extraction. 2024;6(2):1243-62.
[4] Bours MJ. Bayes' rule in diagnosis. J Clin Epidemiol. 2021;131:158-60.
[5] von Brevern M, Bertholon P, Brandt T, Fife T, Imai T, Nuti D, et al. Benign paroxysmal positional vertigo: Diagnostic criteria. J Vestib Res. 2015;25(3-4):105-17.
[6] Bhattacharyya N, Gubbels SP, Schwartz SR, Edlow JA, El-Kashlan H, Fife T, et al. Clinical Practice Guideline: Benign Paroxysmal Positional Vertigo (Update). Otolaryngol Head Neck Surg. 2017;156(3_suppl):S1-S47.
[7] Macdonald NK, Kaski D, Saman Y, Al-Shaikh Sulaiman A, Anwer A, Bamiou DE. Central Positional Nystagmus: A Systematic Literature Review. Front Neurol. 2017;8:141.
[8] Lopez-Escamez JA, Carey J, Chung WH, Goebel JA, Magnusson M, Mandala M, et al. Diagnostic criteria for Meniere's disease. J Vestib Res. 2015;25(1):1-7.
[9] Basura GJ, Adams ME, Monfared A, Schwartz SR, Antonelli PJ, Burkard R, et al. Clinical Practice Guideline: Meniere's Disease. Otolaryngol Head Neck Surg. 2020;162(2_suppl):S1-S55.
[10] Nam DW. Vestibular-GenBN: An open-source framework for modular generative Bayesian networks in vestibular diagnostic knowledge engineering. Version 0.1.3 [software]. Zenodo; 2026. https://doi.org/10.5281/zenodo.20460819.
 
