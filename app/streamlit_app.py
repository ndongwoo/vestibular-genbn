from __future__ import annotations

from pathlib import Path
from typing import Any
import json

import pandas as pd
import streamlit as st

from vestibular_genbn import load_knowledge_bundle
from vestibular_genbn.audit import summarize_audits
from vestibular_genbn.inference import flatten_result, load_case_csv, run_case
from vestibular_genbn.sensitivity import one_way_likelihood_sensitivity
from vestibular_genbn.visualization import build_knowledge_graph, export_mermaid

st.set_page_config(page_title="Vestibular-GenBN", layout="wide")


# ---------------------------------------------------------------------
# Loading utilities
# ---------------------------------------------------------------------

repo_root = Path(__file__).resolve().parents[1]
knowledge_root = repo_root / "knowledge" / "default_v0_1"
examples_file = repo_root / "examples" / "synthetic_cases.csv"
sensitivity_file = knowledge_root / "config" / "sensitivity_ranges.json"


@st.cache_resource
def cached_bundle() -> Any:
    return load_knowledge_bundle(knowledge_root)


@st.cache_data
def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_modules() -> dict[str, dict[str, Any]]:
    modules_dir = knowledge_root / "modules"
    modules: dict[str, dict[str, Any]] = {}

    for path in sorted(modules_dir.glob("*.json")):
        module = read_json(path)
        module_id = module.get("module_id", path.stem)

        # The future placeholder module is informative but not a case-entry module.
        if module_id == "future_placeholder_disease_module":
            continue

        modules[module_id] = module

    return modules


@st.cache_data
def load_all_knowledge_json_files() -> dict[str, Path]:
    return {
        str(path.relative_to(knowledge_root)): path
        for path in sorted(knowledge_root.rglob("*.json"))
    }


@st.cache_data
def load_sensitivity_config() -> dict[str, Any] | None:
    if not sensitivity_file.exists():
        return None
    return read_json(sensitivity_file)


bundle = cached_bundle()
modules = load_modules()
observation_map = {node["id"]: node for node in bundle.observation_nodes}
disease_map = {node["id"]: node for node in bundle.disease_nodes}
finding_map = {node["id"]: node for node in bundle.finding_patterns}


# ---------------------------------------------------------------------
# Table helpers
# ---------------------------------------------------------------------

BINARY_STATES = {"yes", "no", "unknown"}


def as_joined(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def disease_table() -> pd.DataFrame:
    active = set(bundle.active_disease_ids)
    return pd.DataFrame(
        [
            {
                "id": node.get("id"),
                "label": node.get("label", node.get("id")),
                "short_name": node.get("short_name", ""),
                "family": node.get("family", ""),
                "status": node.get("status", ""),
                "active": node.get("id") in active,
                "posterior_mode": node.get("posterior_mode", ""),
            }
            for node in bundle.disease_nodes
        ]
    )


def observation_table() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "id": node.get("id"),
                "label": node.get("label", node.get("id")),
                "group": node.get("group", ""),
                "states": as_joined(node.get("states", [])),
                "description": node.get("description", ""),
            }
            for node in bundle.observation_nodes
        ]
    )


def finding_table() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for node in bundle.finding_patterns:
        rows.append(
            {
                "id": node.get("id"),
                "label": node.get("label", node.get("id")),
                "group": node.get("group", ""),
                "group_type": node.get("group_type", ""),
                "components": as_joined(node.get("components", [])),
                "levels": as_joined([level.get("node") for level in node.get("levels", [])]),
                "description": node.get("description", ""),
            }
        )
    return pd.DataFrame(rows)


def likelihood_table() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for row in bundle.likelihood_rows:
        p1 = float(row["p_finding_true_given_disease_true"])
        p0 = float(row["p_finding_true_given_disease_false"])
        rows.append(
            {
                "disease_node": row["disease_node"],
                "disease_label": disease_map.get(row["disease_node"], {}).get(
                    "label", row["disease_node"]
                ),
                "finding_node": row["finding_node"],
                "finding_label": finding_map.get(row["finding_node"], {}).get(
                    "label", row["finding_node"]
                ),
                "time_slice": row.get("time_slice", ""),
                "p1_P_finding_given_disease": p1,
                "p0_P_finding_given_not_disease": p0,
                "LR_positive": p1 / p0 if p0 > 0 else None,
                "LR_negative": (1.0 - p1) / (1.0 - p0) if p0 < 1 else None,
                "evidence_quality": row.get("evidence_quality", ""),
                "use": row.get("use", ""),
                "notes": row.get("notes", ""),
            }
        )
    return pd.DataFrame(rows)


def detailed_result_dict(
    result: dict[str, Any], raw_case: dict[str, Any], audits: dict[str, Any]
) -> dict[str, Any]:
    return {
        "case_id": result["case_id"],
        "raw_inputs": {
            key: value
            for key, value in raw_case.items()
            if key not in {"case_id", "id"} and str(value).strip() != ""
        },
        "evaluated_finding_values": result["values"],
        "posterior_sum": result["posterior_sum"],
        "normalized_across_diseases": result["normalized_across_diseases"],
        "disease_posteriors": [
            {
                "rank": i,
                "disease_node": posterior.disease_node,
                "prior": posterior.prior,
                "posterior": posterior.posterior,
                "log_odds": posterior.log_odds,
                "n_contributions": len(posterior.contributions),
                "contributions": [
                    {
                        "finding_node": contribution.finding_node,
                        "observed_value": contribution.observed_value,
                        "p_finding_true_given_disease_true": contribution.p_finding_true_given_disease_true,
                        "p_finding_true_given_disease_false": contribution.p_finding_true_given_disease_false,
                        "likelihood_ratio": contribution.likelihood_ratio,
                        "log_likelihood_ratio": contribution.log_likelihood_ratio,
                        "use": contribution.use,
                    }
                    for contribution in posterior.contributions
                ],
            }
            for i, posterior in enumerate(result["disease_posteriors"], start=1)
        ],
        "audit_action_flags": audits,
    }


# ---------------------------------------------------------------------
# Input helpers
# ---------------------------------------------------------------------


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


def observation_input(node: dict[str, Any], *, default: str, key_prefix: str) -> str:
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
            node["id"] for node in bundle.observation_nodes if node.get("group") in safety_groups
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
# Header and sidebar case input
# ---------------------------------------------------------------------

st.title("Vestibular-GenBN demonstration")
st.warning(
    "Research and educational demonstration only. "
    "Not a validated clinical decision-support system."
)

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
    preset_case = next(row for row in preset_rows if row.get("case_id") == selected_preset_name)

key_prefix = selected_preset_name.replace(" ", "_").replace("/", "_")
case_id_default = preset_case.get("case_id", "streamlit_case")
case_id = st.sidebar.text_input("Case ID", value=case_id_default, key=f"{key_prefix}_case_id")
case: dict[str, str] = {"case_id": case_id}

st.sidebar.header("Batch input")
uploaded_csv = st.sidebar.file_uploader(
    "Optional: upload case CSV",
    type=["csv"],
)

selected_observation_ids = get_observation_ids_for_modules(
    selected_module_ids,
    include_safety=include_safety,
    include_supportive_tests=include_supportive_tests,
    include_all=include_all,
)

grouped_nodes = group_observation_ids(selected_observation_ids)

st.sidebar.header("Observation editor")
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

result = run_case(bundle, case)
audits = summarize_audits(bundle, result)


# ---------------------------------------------------------------------
# Main tabs
# ---------------------------------------------------------------------

tabs = st.tabs(
    [
        "Overview",
        "Knowledge bundle viewer",
        "Case simulator",
        "Likelihood table / evidence metadata",
        "Sensitivity analysis",
        "Network export",
    ]
)


with tabs[0]:
    st.subheader("Overview")
    manifest = bundle.manifest
    core_design = manifest.get("core_design", {})

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Bundle version", manifest.get("version", "unknown"))
    col2.metric("Active diseases", len(bundle.active_disease_ids))
    col3.metric("Raw observations", len(bundle.observation_nodes))
    col4.metric("Likelihood rows", len(bundle.likelihood_rows))

    st.markdown(
        "Vestibular-GenBN represents vestibular diagnostic knowledge as modular "
        "generative Bayesian-network knowledge bundles. Disease posteriors are "
        "computed independently and are not normalized across candidate diseases."
    )

    design_df = pd.DataFrame(
        [{"field": key, "value": as_joined(value)} for key, value in core_design.items()]
    )
    st.dataframe(design_df, width='stretch')

    st.subheader("Module summary")
    module_df = pd.DataFrame(
        [
            {
                "module_id": module_id,
                "display_name": module.get("display_name", module_id),
                "version": module.get("version", ""),
                "status": module.get("status", ""),
                "disease_nodes": as_joined(module.get("disease_nodes", [])),
                "primary_raw_observation_nodes": len(
                    module.get("primary_raw_observation_nodes", [])
                ),
                "primary_finding_patterns": len(module.get("primary_finding_patterns", [])),
            }
            for module_id, module in modules.items()
        ]
    )
    st.dataframe(module_df, width='stretch')

    st.subheader("Uploaded batch demonstration")
    if uploaded_csv is None:
        st.info("Upload a CSV in the sidebar to run multiple cases in batch mode.")
    else:
        uploaded_df = pd.read_csv(uploaded_csv).fillna("")
        batch_results = []
        for _, row in uploaded_df.iterrows():
            row_case = {k: str(v) for k, v in row.to_dict().items()}
            batch_result = run_case(bundle, row_case)
            top = batch_result["disease_posteriors"][0]
            batch_results.append(
                {
                    "case_id": batch_result["case_id"],
                    "top_disease": top.disease_node,
                    "top_posterior": round(top.posterior, 4),
                    "posterior_sum": round(batch_result["posterior_sum"], 4),
                    "normalized_across_diseases": batch_result["normalized_across_diseases"],
                }
            )
        st.dataframe(pd.DataFrame(batch_results), width='stretch')


with tabs[1]:
    st.subheader("Knowledge bundle viewer")

    viewer_tab1, viewer_tab2, viewer_tab3, viewer_tab4 = st.tabs(
        ["Modules", "Registries", "Raw JSON", "Manifest"]
    )

    with viewer_tab1:
        selected_module = st.selectbox(
            "Select module",
            options=list(modules.keys()),
            format_func=lambda module_id: modules[module_id].get("display_name", module_id),
        )
        module = modules[selected_module]
        c1, c2, c3 = st.columns(3)
        c1.metric("Disease nodes", len(module.get("disease_nodes", [])))
        c2.metric("Raw observation nodes", len(module.get("primary_raw_observation_nodes", [])))
        c3.metric("Finding patterns", len(module.get("primary_finding_patterns", [])))

        st.markdown("**Disease nodes**")
        st.dataframe(
            disease_table()[disease_table()["id"].isin(module.get("disease_nodes", []))],
            width='stretch',
        )

        st.markdown("**Primary raw observation nodes**")
        st.dataframe(
            observation_table()[
                observation_table()["id"].isin(module.get("primary_raw_observation_nodes", []))
            ],
            width='stretch',
        )

        st.markdown("**Primary finding patterns**")
        st.dataframe(
            finding_table()[finding_table()["id"].isin(module.get("primary_finding_patterns", []))],
            width='stretch',
        )

        with st.expander("Module JSON"):
            st.json(module)

    with viewer_tab2:
        registry = st.radio(
            "Registry",
            options=["Disease nodes", "Raw observations", "Finding patterns"],
            horizontal=True,
        )
        if registry == "Disease nodes":
            st.dataframe(disease_table(), width='stretch')
        elif registry == "Raw observations":
            groups = sorted(observation_table()["group"].dropna().unique().tolist())
            selected_groups = st.multiselect("Observation groups", groups, default=groups)
            df = observation_table()
            st.dataframe(df[df["group"].isin(selected_groups)], width='stretch')
        else:
            st.dataframe(finding_table(), width='stretch')

    with viewer_tab3:
        json_files = load_all_knowledge_json_files()
        selected_json = st.selectbox("Knowledge JSON file", options=list(json_files.keys()))
        st.json(read_json(json_files[selected_json]))

    with viewer_tab4:
        st.json(bundle.manifest)


with tabs[2]:
    st.subheader("Case simulator")

    st.markdown("### Independent disease posteriors")
    posterior_df = pd.DataFrame(
        [
            {
                "rank": i,
                "disease_node": posterior.disease_node,
                "prior": round(posterior.prior, 4),
                "posterior": round(posterior.posterior, 4),
                "n_contributions": len(posterior.contributions),
            }
            for i, posterior in enumerate(result["disease_posteriors"], start=1)
        ]
    )
    st.dataframe(posterior_df, width='stretch')
    st.caption(
        f"Posterior sum = {result['posterior_sum']:.3f}. "
        "This is not normalized across disease nodes."
    )

    st.markdown("### Audit/action overlay")
    st.json(audits)

    st.markdown("### Evidence contributions by disease")
    selected_disease = st.selectbox(
        "Select disease node",
        [posterior.disease_node for posterior in result["disease_posteriors"]],
    )
    selected_posterior = next(
        posterior
        for posterior in result["disease_posteriors"]
        if posterior.disease_node == selected_disease
    )
    contrib_df = pd.DataFrame(
        [
            {
                "finding_node": contribution.finding_node,
                "observed_value": contribution.observed_value,
                "LR": round(contribution.likelihood_ratio, 4),
                "log_LR": round(contribution.log_likelihood_ratio, 4),
                "P(finding|disease)": contribution.p_finding_true_given_disease_true,
                "P(finding|not disease)": contribution.p_finding_true_given_disease_false,
                "use": contribution.use,
            }
            for contribution in selected_posterior.contributions
        ]
    )
    if contrib_df.empty:
        st.info("No observed finding contributed to this disease posterior.")
    else:
        st.dataframe(contrib_df, width='stretch')

    left, right = st.columns(2)
    with left:
        st.markdown("### Current raw input case")
        input_df = pd.DataFrame([{"node": k, "value": v} for k, v in sorted(case.items())])
        st.dataframe(input_df, width='stretch')
    with right:
        st.markdown("### Evaluated finding values")
        values_df = pd.DataFrame(
            [{"node": k, "value": v} for k, v in sorted(result["values"].items())]
        )
        st.dataframe(values_df, width='stretch')

    st.markdown("### Export current case/result")
    case_df = pd.DataFrame([case])
    detail = detailed_result_dict(result, case, audits)
    c1, c2, c3 = st.columns(3)
    c1.download_button(
        "Download current case CSV",
        data=case_df.to_csv(index=False).encode("utf-8"),
        file_name=f"{case_id}.csv",
        mime="text/csv",
    )
    c2.download_button(
        "Download posterior summary CSV",
        data=pd.DataFrame(flatten_result(result)).to_csv(index=False).encode("utf-8"),
        file_name=f"{case_id}_posterior_summary.csv",
        mime="text/csv",
    )
    c3.download_button(
        "Download detailed JSON",
        data=json.dumps(detail, ensure_ascii=False, indent=2).encode("utf-8"),
        file_name=f"{case_id}_detailed.json",
        mime="application/json",
    )


with tabs[3]:
    st.subheader("Likelihood table / evidence metadata")

    df = likelihood_table()
    diseases = sorted(df["disease_node"].unique().tolist())
    evidence_types = sorted(df["evidence_quality"].dropna().unique().tolist())

    c1, c2 = st.columns(2)
    selected_diseases = c1.multiselect("Disease nodes", diseases, default=diseases)
    selected_evidence_types = c2.multiselect(
        "Evidence quality", evidence_types, default=evidence_types
    )

    filtered_df = df[
        df["disease_node"].isin(selected_diseases)
        & df["evidence_quality"].isin(selected_evidence_types)
    ]
    st.dataframe(filtered_df, width='stretch')

    st.download_button(
        "Download likelihood table CSV",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="vestibular_genbn_likelihood_table.csv",
        mime="text/csv",
    )

    if not filtered_df.empty:
        row_labels = [
            f"{row.disease_node} | {row.finding_node}"
            for row in filtered_df.itertuples(index=False)
        ]
        selected_row_label = st.selectbox("Inspect likelihood row", row_labels)
        selected_index = row_labels.index(selected_row_label)
        st.json(filtered_df.iloc[selected_index].to_dict())


with tabs[4]:
    st.subheader("Sensitivity analysis")
    st.caption(
        "The current utility varies p1 = P(finding=true | disease=true) "
        "while holding p0 fixed at the seed value."
    )

    config = load_sensitivity_config()
    settings = config.get("parameters", []) if config else []

    if settings:
        setting_labels = [
            f"{item['id']} ({item['disease_node']} | {item['finding_node']})" for item in settings
        ]
        selected_setting_label = st.selectbox("Configured sensitivity target", setting_labels)
        setting = settings[setting_labels.index(selected_setting_label)]
        sensitivity_disease = setting["disease_node"]
        sensitivity_finding = setting["finding_node"]
        default_values = ", ".join(str(v) for v in setting["p1_values"])
        st.markdown(f"**Rationale:** {setting.get('rationale', '')}")
    else:
        st.info(
            "No sensitivity_ranges.json file was found. "
            "Manual disease/finding selection is available."
        )
        sensitivity_disease = st.selectbox("Disease node", bundle.active_disease_ids)
        available_findings = sorted(
            row["finding_node"]
            for row in bundle.likelihood_rows
            if row["disease_node"] == sensitivity_disease
        )
        sensitivity_finding = st.selectbox("Finding node", available_findings)
        default_values = "0.7, 0.8, 0.9"

    p1_text = st.text_input(
        "p1 values to evaluate",
        value=default_values,
        help="Comma-separated values between 0 and 1.",
    )

    try:
        p1_values = [float(value.strip()) for value in p1_text.split(",") if value.strip()]
        if not p1_values or not all(0.0 < value < 1.0 for value in p1_values):
            raise ValueError
    except ValueError:
        st.error("Enter comma-separated p1 values between 0 and 1, such as 0.7, 0.8, 0.9.")
        p1_values = []

    if p1_values:
        sensitivity_rows = one_way_likelihood_sensitivity(
            bundle,
            case,
            disease_node=sensitivity_disease,
            finding_node=sensitivity_finding,
            p1_values=p1_values,
        )
        sensitivity_df = pd.DataFrame(sensitivity_rows)
        st.dataframe(sensitivity_df, width='stretch')
        st.line_chart(sensitivity_df.set_index("p1")[["posterior"]])

        st.download_button(
            "Download sensitivity results CSV",
            data=sensitivity_df.to_csv(index=False).encode("utf-8"),
            file_name=f"sensitivity_{sensitivity_disease}_{sensitivity_finding}.csv",
            mime="text/csv",
        )


with tabs[5]:
    st.subheader("Network export")
    graph = build_knowledge_graph(bundle)
    c1, c2, c3 = st.columns(3)
    c1.metric("Graph nodes", graph.number_of_nodes())
    c2.metric("Graph edges", graph.number_of_edges())
    c3.metric("Active disease nodes", len(bundle.active_disease_ids))

    mermaid = export_mermaid(bundle)
    st.markdown("### Mermaid flowchart")
    st.code(mermaid, language="mermaid")
    st.download_button(
        "Download Mermaid network",
        data=mermaid.encode("utf-8"),
        file_name="vestibular_genbn_network.mmd",
        mime="text/plain",
    )

    edge_df = pd.DataFrame(
        [
            {
                "source": source,
                "target": target,
                "kind": data.get("kind", ""),
            }
            for source, target, data in graph.edges(data=True)
        ]
    )
    st.markdown("### Edge table")
    st.dataframe(edge_df, width='stretch')
    st.download_button(
        "Download edge table CSV",
        data=edge_df.to_csv(index=False).encode("utf-8"),
        file_name="vestibular_genbn_network_edges.csv",
        mime="text/csv",
    )
