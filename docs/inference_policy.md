# Inference policy

Vestibular-GenBN uses independent binary/multi-label disease posteriors.

For each disease node:

```text
posterior odds = prior odds × product(likelihood ratios for observed findings)
```

Disease posteriors are not normalized across disease nodes. The posterior sum may be less than,
equal to, or greater than 1. Ranking is allowed, but the ranked outputs are not a probability
simplex.
