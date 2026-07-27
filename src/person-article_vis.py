import streamlit as st
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle
import json
from pathlib import Path

st.set_page_config(layout="wide")

DATA_DIR = Path("../data")
GRAPH_PATH = DATA_DIR / "graph_output.json"


@st.cache_data(show_spinner=False)
def load_graph(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


elements = load_graph(GRAPH_PATH)

if not elements.get("nodes") or not elements.get("edges"):
    st.error("The graph file does not contain any nodes or edges to display.")
    st.stop()

node_styles = [
    NodeStyle("PERSON", "#FF7F3E", "name", "person"),
    NodeStyle("ARTICLE", "#2A629A", "name", "document"),
]

edge_styles = [
    EdgeStyle("MENTIONS_ARTICLE", labeled=False, directed=False),
]

layout = {"name": "cose", "animate": "end", "nodeDimensionsIncludeLabels": False}

st.markdown("### Person–Article network")
st_link_analysis(
    elements,
    node_styles=node_styles,
    edge_styles=edge_styles,
    layout=layout,
    key="person_article_graph",
)
