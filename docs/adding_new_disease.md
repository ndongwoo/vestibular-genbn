# Adding a new disease

To activate a placeholder disease:

1. Change its disease-node `status` from `placeholder` to `active`.
2. Add missing raw observations to the global observation registry.
3. Add derived finding patterns.
4. Add disease-specific likelihood rows.
5. Add the disease node to `active_disease_nodes`.
6. Add criteria/action rules only if needed.

Do not add an `alternative diagnosis` raw node. Competing explanations are handled after
posterior calculation using independent posterior thresholds.
