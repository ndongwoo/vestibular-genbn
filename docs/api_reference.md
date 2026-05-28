# API reference

```python
from vestibular_genbn import load_knowledge_bundle
from vestibular_genbn.inference import run_case

bundle = load_knowledge_bundle("knowledge/default_v0_1")
result = run_case(bundle, {"case_id": "demo", "hx_positional_trigger": "yes"})
```
