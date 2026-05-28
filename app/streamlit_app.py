from __future__ import annotations

from pathlib import Path
import json

import pandas as pd
import streamlit as st

from vestibular_genbn import load_knowledge_bundle
from vestibular_genbn.audit import summarize_audits
from vestibular_genbn.inference import load_case_csv, run_case


st.set_page_config(page_title="Vestibular-GenBN", layout="wide")

st.title("Vestibular-GenBN demonstration")
st.warning(
    "Research and educational demonstration only. "
    "Not a validated clinical decision-support system."
)


# ---------------------------------------------------------------------
# Loading utilities
# ---------------------------------------------------------------------

repo_root = Path(__file__).resolve().parents[1]
knowledge_root = repo_root / "knowledge" / "default_v0_1"
examples_file = repo_root / "examples" / "synthetic_cases.csv"

bundle = load_knowledge_bundle(knowledge_root)


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_modules() -> dict[str, dict]:
    modules_dir = knowledge_root / "modules"
    modules: dict[str, dict] = {}

    for path in sorted(modules_dir.glob("*.json")):
        module = read_json(path)
        module_id = module.get("module_id", path.stem)

        # The future placeholder module is not a case-entry module.
        if module_id == "future_placeholder_disease_module":
            continue

        modules[module_id] = module

    return modules


modules = load_modules()
observation_map = {node["id"]: node for node in bundle.observation_nodes}


# ---------------------------------------------------------------------
# UI rendering utilities
# ---------------------------------------------------------------------

BINARY_STATES = {"yes", "no", "unknown"}


def normalize_default(value: object, states: list[str]) -> str:
    if value is None:
        return "unknown" if "unknown" in states else states[0]

    value = str(value).strip()

    if value == "":
        return "unknown" if "unknown" in states else states[0]

    if value in states:
        return value

    return "unknown" if "unknown" in states else states[0]


def tri_state_input(label: str, key: str, default: str = "unknown") -> str:
    options = ["unknown", "yes", "no"]
    labels = {
        "unknown": "Unknown / not assessed",
        "yes": "Yes / present",
        "no": "No / absent",
    }

    return st.radio(
        label,
        options=options,
        index=options.index(default),
        format_func=lambda x: labels[x],
        horizontal=True,
        key=key,
    )


def observation_input(node: dict, *, default: str, key_prefix: str) -> str:
    node_id = node["id"]
    label = node.get("label", node_id)
    states = list(node.get("states", ["yes", "no", "unknown"]))
    default = normalize_default(default, states)

    key = f"{key_prefix}_{node_id}"

    if set(states) == BINARY_STATES:
        return tri_state_input(label, key=key, default=default)

    return st.selectbox(
        label,
        options=states,
        index=states.index(default),
        key=key,
    )


def get_observation_ids_for_modules(
    selected_module_ids: list[str],
    *,
    include_safety: bool,
    include_supportive_tests: bool,
    include_all: bool,
) -> list[str]:
    if include_all:
        return [node["id"] for node in bundle.observation_nodes]

    ids: list[str] = []

    for module_id in selected_module_ids:
        module = modules[module_id]
        ids.extend(module.get("primary_raw_observation_nodes", []))

    if include_safety:
        safety_groups = {
            "central_safety",
            "central_positional_screen",
            "imaging",
        }
        ids.extend(
            node["id"]
            for node in bundle.observation_nodes
            if node.get("group") in safety_groups
        )

    if include_supportive_tests:
        supportive_groups = {
            "vestibular_lab",
            "audiovestibular_lab",
            "imaging",
        }
        ids.extend(
            node["id"]
            for node in bundle.observation_nodes
            if node.get("group") in supportive_groups
        )

    # Keep order while removing duplicates.
    seen = set()
    ordered = []
    for node_id in ids:
        if node_id in observation_map and node_id not in seen:
            ordered.append(node_id)
            seen.add(node_id)

    return ordered


def group_observation_ids(node_ids: list[str]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}

    for node_id in node_ids:
        node = observation_map[node_id]
        group = node.get("group", "other")
        grouped.setdefault(group, []).append(node_id)

    return grouped


# ---------------------------------------------------------------------
# Sidebar: module selection and case preset
# ---------------------------------------------------------------------

st.sidebar.header("Case input")

st.sidebar.caption(
    "Use **Unknown** when the item was not assessed or not documented. "
    "Use **No** only when absence was explicitly confirmed."
)

module_options = list(modules.keys())
selected_module_ids = st.sidebar.multiselect(
    "Active input modules",
    options=module_options,
    default=module_options,
    format_func=lambda module_id: modules[module_id].get("display_name", module_id),
)

include_safety = st.sidebar.checkbox(
    "Include shared safety / central red-flag observations",
    value=True,
)

include_supportive_tests = st.sidebar.checkbox(
    "Include supportive vestibular/audiologic/imaging tests",
    value=False,
)

include_all = st.sidebar.checkbox(
    "Show all raw observation nodes",
    value=False,
)

# ---------------------------------------------------------------------
# Preset cases from examples/synthetic_cases.csv
# ---------------------------------------------------------------------

preset_rows: list[dict[str, str]] = []
if examples_file.exists():
    preset_rows = load_case_csv(examples_file)

preset_names = ["Blank case"] + [
    str(row.get("case_id", f"case_{i}")) for i, row in enumerate(preset_rows, start=1)
]

selected_preset_name = st.sidebar.selectbox(
    "Load synthetic case preset",
    options=preset_names,
    index=0,
)

if selected_preset_name == "Blank case":
    preset_case: dict[str, str] = {}
else:
    preset_case = next(
        row for row in preset_rows if row.get("case_id") == selected_preset_name
    )

# Include preset name in widget keys so changing preset resets defaults.
key_prefix = selected_preset_name.replace(" ", "_").replace("/", "_")

case_id_default = preset_case.get("case_id", "streamlit_case")
case_id = st.sidebar.text_input("Case ID", value=case_id_default, key=f"{key_prefix}_case_id")

case: dict[str, str] = {"case_id": case_id}

# ---------------------------------------------------------------------
# Optional CSV upload for batch-style demonstration
# ---------------------------------------------------------------------

st.sidebar.header("Batch input")
uploaded_csv = st.sidebar.file_uploader(
    "Optional: upload case CSV",
    type=["csv"],
)

if uploaded_csv is not None:
    uploaded_df = pd.read_csv(uploaded_csv).fillna("")
    st.subheader("Uploaded batch cases")

    batch_results = []
    for _, row in uploaded_df.iterrows():
        row_case = {k: str(v) for k, v in row.to_dict().items()}
        result = run_case(bundle, row_case)
        top = result["disease_posteriors"][0]
        batch_results.append(
            {
                "case_id": result["case_id"],
                "top_disease": top.disease_node,
                "top_posterior": round(top.posterior, 4),
                "posterior_sum": round(result["posterior_sum"], 4),
                "normalized_across_diseases": result["normalized_across_diseases"],
            }
        )

    st.dataframe(pd.DataFrame(batch_results), width='stretch')
    st.stop()


# ---------------------------------------------------------------------
# Auto-generated observation form
# ---------------------------------------------------------------------

selected_observation_ids = get_observation_ids_for_modules(
    selected_module_ids,
    include_safety=include_safety,
    include_supportive_tests=include_supportive_tests,
    include_all=include_all,
)

st.sidebar.header("Observation editor")

grouped_nodes = group_observation_ids(selected_observation_ids)

for group, node_ids in grouped_nodes.items():
    with st.sidebar.expander(group, expanded=True):
        for node_id in node_ids:
            node = observation_map[node_id]
            default_value = preset_case.get(node_id, "unknown")
            case[node_id] = observation_input(
                node,
                default=default_value,
                key_prefix=key_prefix,
            )


# ---------------------------------------------------------------------
# Run inference
# ---------------------------------------------------------------------

result = run_case(bundle, case)
audits = summarize_audits(bundle, result)

# ---------------------------------------------------------------------
# Main output
# ---------------------------------------------------------------------

st.subheader("Independent disease posteriors")

posterior_df = pd.DataFrame(
    [
        {
            "rank": i,
            "disease_node": p.disease_node,
            "prior": round(p.prior, 4),
            "posterior": round(p.posterior, 4),
            "n_contributions": len(p.contributions),
        }
        for i, p in enumerate(result["disease_posteriors"], start=1)
    ]
)

st.dataframe(posterior_df, width='stretch')

st.caption(
    f"Posterior sum = {result['posterior_sum']:.3f}. "
    "This is not normalized across disease nodes."
)

st.subheader("Audit/action overlay")
st.json(audits)

# ---------------------------------------------------------------------
# Evidence contribution inspection
# ---------------------------------------------------------------------

st.subheader("Evidence contributions by disease")

selected_disease = st.selectbox(
    "Select disease node",
    [p.disease_node for p in result["disease_posteriors"]],
)

selected_posterior = next(
    p for p in result["disease_posteriors"] if p.disease_node == selected_disease
)

contrib_df = pd.DataFrame(
    [
        {
            "finding_node": c.finding_node,
            "observed_value": c.observed_value,
            "LR": round(c.likelihood_ratio, 4),
            "log_LR": round(c.log_likelihood_ratio, 4),
            "P(finding|disease)": c.p_finding_true_given_disease_true,
            "P(finding|not disease)": c.p_finding_true_given_disease_false,
            "use": c.use,
        }
        for c in selected_posterior.contributions
    ]
)

if contrib_df.empty:
    st.info("No observed finding contributed to this disease posterior.")
else:
    st.dataframe(contrib_df, width='stretch')


# ---------------------------------------------------------------------
# Case and finding inspection
# ---------------------------------------------------------------------

left, right = st.columns(2)

with left:
    st.subheader("Current raw input case")
    input_df = pd.DataFrame(
        [{"node": k, "value": v} for k, v in sorted(case.items())]
    )
    st.dataframe(input_df, width='stretch')

with right:
    st.subheader("Evaluated finding values")
    values_df = pd.DataFrame(
        [{"node": k, "value": v} for k, v in sorted(result["values"].items())]
    )
    st.dataframe(values_df, width='stretch')


# ---------------------------------------------------------------------
# Download current case
# ---------------------------------------------------------------------

st.subheader("Export current case")

case_df = pd.DataFrame([case])
st.download_button(
    "Download current case as CSV",
    data=case_df.to_csv(index=False).encode("utf-8"),
    file_name=f"{case_id}.csv",
    mime="text/csv",
)