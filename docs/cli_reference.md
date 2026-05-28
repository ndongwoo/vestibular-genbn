# CLI reference

Validate a bundle:

```bash
vestibular-genbn validate knowledge/default_v0_1
```

Run synthetic cases:

```bash
vestibular-genbn run --case-file examples/synthetic_cases.csv --knowledge knowledge/default_v0_1
```

List diseases:

```bash
vestibular-genbn list-diseases knowledge/default_v0_1
```

Export Mermaid network:

```bash
vestibular-genbn export-network knowledge/default_v0_1 --output docs/network.mmd
```
