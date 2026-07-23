import json
from pathlib import Path

import streamlit as st
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle

st.set_page_config(layout="wide")

GRAPH_PATH = Path(__file__).with_name("graph_output.json")


def clean_edges(elements):
    if "edges" not in elements:
        return elements

    elements["edges"] = [
        edge
        for edge in elements["edges"]
        if edge.get("data", {}).get("source") != edge.get("data", {}).get("target")
    ]
    return elements


def node_label(node):
    data = node.get("data", {})
    node_id = data.get("id")
    name = data.get("name") or data.get("label") or "UNKNOWN"
    return f"#{node_id} | {name}"


def edge_label(edge):
    data = edge.get("data", {})
    edge_id = data.get("id")
    source = data.get("source")
    target = data.get("target")
    label = data.get("label", "UNKNOWN")
    score = data.get("score")
    return f"#{edge_id} | {source} -> {target} | {label} | score={score}"


def sort_ids(ids):
    def sort_key(item_id):
        try:
            return (0, int(item_id))
        except (TypeError, ValueError):
            return (1, str(item_id))

    return sorted(ids, key=sort_key)


def delete_selected_edges(elements, selected_edge_ids):
    if not selected_edge_ids:
        return elements, 0

    selected_edge_ids_set = {str(edge_id) for edge_id in selected_edge_ids}
    original_edge_count = len(elements.get("edges", []))
    elements["edges"] = [
        edge
        for edge in elements.get("edges", [])
        if str(edge.get("data", {}).get("id")) not in selected_edge_ids_set
    ]
    st.session_state["elements"] = elements
    return elements, original_edge_count - len(elements.get("edges", []))


def delete_selected_nodes(elements, selected_node_ids):
    if not selected_node_ids:
        return elements, 0

    selected_node_ids_set = {str(node_id) for node_id in selected_node_ids}
    original_node_count = len(elements.get("nodes", []))
    original_edge_count = len(elements.get("edges", []))

    elements["nodes"] = [
        node
        for node in elements.get("nodes", [])
        if str(node.get("data", {}).get("id")) not in selected_node_ids_set
    ]

    elements["edges"] = [
        edge
        for edge in elements.get("edges", [])
        if str(edge.get("data", {}).get("source")) not in selected_node_ids_set
        and str(edge.get("data", {}).get("target")) not in selected_node_ids_set
    ]

    st.session_state["elements"] = elements
    return elements, original_node_count - len(elements.get("nodes", [])), original_edge_count - len(elements.get("edges", []))


# Load the data
with GRAPH_PATH.open("r", encoding="utf-8") as f:
    initial_elements = json.load(f)

clean_edges(initial_elements)

if "elements" not in st.session_state:
    st.session_state["elements"] = initial_elements

elements = st.session_state["elements"]
clean_edges(elements)

node_lookup = {
    str(node.get("data", {}).get("id")): node
    for node in elements.get("nodes", [])
    if node.get("data", {}).get("id") is not None
}

node_ids = sort_ids(node_lookup.keys())

edge_lookup = {
    str(edge.get("data", {}).get("id")): edge
    for edge in elements.get("edges", [])
    if edge.get("data", {}).get("id") is not None
}

edge_ids = sort_ids(edge_lookup.keys())

st.sidebar.title("Graph editor")
st.sidebar.caption("Delete graph elements here and save the updated JSON when you are done.")

selected_node_ids = st.sidebar.multiselect(
    "Nodes to delete",
    options=node_ids,
    format_func=lambda node_id: node_label(node_lookup[node_id]),
)

if st.sidebar.button("Delete selected nodes"):
    if selected_node_ids:
        _, deleted_nodes, deleted_edges = delete_selected_nodes(elements, selected_node_ids)
        st.sidebar.success(
            f"Deleted {deleted_nodes} node(s) and {deleted_edges} incident edge(s) from the in-memory graph."
        )
    else:
        st.sidebar.warning("Select at least one node to delete.")

selected_edge_ids = st.sidebar.multiselect(
    "Edges to delete",
    options=edge_ids,
    format_func=lambda edge_id: edge_label(edge_lookup[edge_id]),
)

if st.sidebar.button("Delete selected edges"):
    if selected_edge_ids:
        _, deleted_edges = delete_selected_edges(elements, selected_edge_ids)
        st.sidebar.success(f"Deleted {deleted_edges} edge(s) from the in-memory graph.")
    else:
        st.sidebar.warning("Select at least one edge to delete.")

st.sidebar.write("Choose where the edited graph should be stored.")
output_path = st.sidebar.text_input("Output JSON path", value=str(GRAPH_PATH))

if st.sidebar.button("Save updated graph"):
    try:
        save_path = Path(output_path)
        with save_path.open("w", encoding="utf-8") as f:
            json.dump(elements, f, indent=2, ensure_ascii=False)
        st.sidebar.success(f"Saved updated graph to: {save_path}")
    except Exception as exc:
        st.sidebar.error(f"Unable to save JSON: {exc}")

st.title("Network visualization")

node_styles = [
    NodeStyle("PERSON", "#2A629B", "name", "cloud"),
]

edge_styles = [
    EdgeStyle("SIMILAR", labeled=False, directed=False),
]

layout = {"name": "cose", "animate": "end", "nodeDimensionsIncludeLabels": False}

st_link_analysis(
    elements,
    node_styles=node_styles,
    edge_styles=edge_styles,
    layout=layout,
    key="xyz",
)