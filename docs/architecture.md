# Architecture

The core workflow is:

1. Load a JSON knowledge bundle.
2. Validate internal references.
3. Read a synthetic or user-supplied case.
4. Evaluate derived finding patterns from raw observations.
5. Compute independent disease posteriors by likelihood-ratio updating.
6. Apply criteria audit and safety/action overlays without modifying posterior probabilities.

```text
raw observations -> finding patterns -> independent disease posteriors -> audit/action overlay
```
