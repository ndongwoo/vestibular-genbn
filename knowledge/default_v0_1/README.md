# Vestibular Generative BN Clean Seed v0.1.3

This package is a clean starting point for a vestibular generative Bayesian network project.

## Core assumptions

- Disease posteriors are computed independently as binary one-vs-rest or multi-label posteriors.
- Posterior probabilities are not normalized to sum to 1 across diseases.
- Candidate sets define which disease nodes are evaluated in a run, not a mutually exclusive diagnostic universe.
- BPPV and Ménière-spectrum modules are active base modules.
- VM, FVD/PPPD, MdDS, AUVP/CUVP, vestibular paroxysmia, presbyvestibulopathy, BVP, hemodynamic dizziness, ototoxic dizziness, medication-induced dizziness, CPA/IAC tumor, central disorder, SCDS, and labyrinthitis are included as placeholders.

## Files

- `project_manifest.json`
- `config/inference_policy_v0_1.json`
- `config/candidate_set_core_v0_1.json`
- `registries/disease_node_registry.json`
- `registries/global_observation_registry.json`
- `registries/global_finding_pattern_registry.json`
- `likelihoods/bppv_meniere_seed_likelihoods.json`
- `audits/criteria_audit_rules.json`
- `audits/posterior_audit_rules.json`
- `audits/safety_action_rules.json`
- `modules/bppv_core_module.json`
- `modules/meniere_core_module.json`
- `modules/future_placeholder_disease_module.json`
- `schemas/minimal_schema_contract.json`

## Activation workflow for a future disease

1. Change the disease node status from `placeholder` to `active`.
2. Add any missing raw observations to `global_observation_registry.json`.
3. Add shared derived finding patterns to `global_finding_pattern_registry.json`.
4. Add disease-specific likelihood rows.
5. Add the disease node to `active_disease_nodes` in the candidate set.
6. Add criteria or action rules only if they are not used as posterior evidence.
