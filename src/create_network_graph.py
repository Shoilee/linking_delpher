# %%
import json
from pathlib import Path
OUTPUT_DIR = Path("../data")

# %%
input_filepath = OUTPUT_DIR / "similar_names.json"
output_filepath = OUTPUT_DIR / "graph_output.json"

# %%
# convert the json object to networkx graph

import json

def convert_to_graph(records):
    node_map = {}
    nodes = []
    edges = []

    # Keep stable IDs
    def add_node(name, label, article):
        if name not in node_map:
            node_id = len(node_map) + 1
            node_map[name] = node_id
            nodes.append({
                "data": {
                    "id": node_id,
                    "label": label,
                    "name": name,
                    "article": article
                }
            })
        return node_map[name]

    edge_id = 1000000 # Start edge IDs from an arbitrary big number to avoid collision with node IDs

    for item in records:
        source_name = item.get("name")
        source_label = item.get("label", "PERSON")
        source_article = item.get("article")

        source_id = add_node(source_name, source_label, source_article)

        for related in item.get("candidates", []):
            target_name = related.get("name")
            target_label = related.get("label", "PERSON") 
            target_article = related.get("article")

            target_id = add_node(target_name, target_label, target_article)

            # Add all related-item fields to the edge data
            tags = {key: value for key, value in related.items() if key not in ["name", "article"]}

            edge_data = {
                "id": edge_id,
                "label": "SIMILAR",
                "source": source_id,
                "target": target_id,
                **{f"{key}": value for key, value in tags.items()}
            }

            edges.append({
                "data": edge_data
            })
            edge_id += 1

    return {
        "nodes": nodes,
        "edges": edges
    }


# Example usage
with open(input_filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

graph = convert_to_graph(data)

with open(output_filepath, "w+", encoding="utf-8") as f:
    json.dump(graph, f, ensure_ascii=False, indent=2)


