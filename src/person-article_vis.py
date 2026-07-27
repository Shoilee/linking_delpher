import streamlit as st
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle
import json
from copy import deepcopy
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

person_nodes = [node for node in elements.get("nodes", []) if node.get("data", {}).get("label") == "PERSON"]
article_nodes = [node for node in elements.get("nodes", []) if node.get("data", {}).get("label") == "ARTICLE"]

person_count = len(person_nodes)
article_count = len(article_nodes)

article_to_persons = {}
for edge in elements.get("edges", []):
    data = edge.get("data", {})
    if data.get("label") != "MENTIONS_ARTICLE":
        continue
    source = data.get("source")
    target = data.get("target")
    source_node = next((node for node in person_nodes if node.get("data", {}).get("id") == source), None)
    target_node = next((node for node in article_nodes if node.get("data", {}).get("id") == target), None)
    if source_node and target_node:
        article_name = target_node.get("data", {}).get("name")
        article_to_persons.setdefault(article_name, set()).add(source_node.get("data", {}).get("name"))

persons_per_article = {article: len(names) for article, names in article_to_persons.items()}
max_persons_in_article = max(persons_per_article.values(), default=0)

with st.sidebar:
    st.header("Graph summary")
    st.metric("Unique persons", person_count)
    st.metric("Unique articles", article_count)
    st.metric("Max persons in one article", max_persons_in_article)

    st.divider()
    st.subheader("Find node")
    search_name = st.text_input("Person or article name", placeholder="Type a person or article name")

highlighted_elements = deepcopy(elements)
matched_node_ids = set()
query = (search_name or "").strip().lower()

if query:
    for node in highlighted_elements.get("nodes", []):
        data = node.get("data", {})
        label = data.get("label")
        name = str(data.get("name") or "").lower()
        alternate_names = [str(value).lower() for value in data.get("alternate_name", []) if value is not None]

        if label == "PERSON":
            if query in name or any(query in alt for alt in alternate_names):
                matched_node_ids.add(data.get("id"))
                data["label"] = "PERSON_HIGHLIGHT"
                data["name"] = f"★ {data.get('name')}"
        elif label == "ARTICLE":
            if query in name:
                matched_node_ids.add(data.get("id"))
                data["label"] = "ARTICLE_HIGHLIGHT"
                data["name"] = f"★ {data.get('name')}"

node_styles = [
    NodeStyle("PERSON", "#FF7F3E", "name", "person"),
    NodeStyle("PERSON_HIGHLIGHT", "#FFD54F", "name", "person"),
    NodeStyle("ARTICLE", "#2A629A", "name", "document"),
    NodeStyle("ARTICLE_HIGHLIGHT", "#4FC3F7", "name", "document"),
]

edge_styles = [
    EdgeStyle("MENTIONS_ARTICLE", caption=False, directed=False),
]

layout = {"name": "cose", "animate": "end", "nodeDimensionsIncludeLabels": False}

st.markdown("### Person–Article network")
if query and not matched_node_ids:
    st.info("No person or article matched that name.")

st_link_analysis(
    highlighted_elements,
    node_styles=node_styles,
    edge_styles=edge_styles,
    layout=layout,
    key="person_article_graph",
)
