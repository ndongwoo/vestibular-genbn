# SoftwareX user guide

Reproducibility checklist:

```bash
pip install -e ".[dev]"
vestibular-genbn validate knowledge/default_v0_1
python examples/run_examples.py
pytest
```

The synthetic cases demonstrate software behavior, not diagnostic accuracy or clinical utility.
