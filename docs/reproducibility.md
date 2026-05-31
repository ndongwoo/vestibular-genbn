git clone https://github.com/ndongwoo/vestibular-genbn.git
cd vestibular-genbn
git checkout v0.1.3
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
vestibular-genbn validate knowledge/default_v0_1
vestibular-genbn run --case-file examples/synthetic_cases.csv --knowledge knowledge/default_v0_1 --output outputs/output_core_v0_1.csv
pytest
