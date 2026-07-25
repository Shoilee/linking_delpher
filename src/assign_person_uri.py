import json
from pathlib import Path

input_path = Path("../data/graph_output.json")
loaded_data = json.loads(input_path.read_text(encoding="utf-8"))

if isinstance(loaded_data, dict):
    data = [
        {"data": item["data"], "group": "nodes"}
        for item in loaded_data.get("nodes", [])
    ] + [
        {"data": item["data"], "group": "edges"}
        for item in loaded_data.get("edges", [])
    ]
else:
    data = loaded_data

nodes = [item for item in data if item.get("group") == "nodes"]
node_by_id = {str(item["data"]["id"]): item for item in nodes}
parent = {node_id: node_id for node_id in node_by_id}

def find(node_id):
    while parent[node_id] != node_id:
        parent[node_id] = parent[parent[node_id]]
        node_id = parent[node_id]
    return node_id

for item in data:
    if item.get("group") != "edges":
        continue

    edge_data = item.get("data", {})
    source = str(edge_data.get("source"))
    target = str(edge_data.get("target"))

    if source in parent and target in parent:
        source_root = find(source)
        target_root = find(target)
        if source_root != target_root:
            parent[source_root] = target_root

components = {}
for node_id in node_by_id:
    components.setdefault(find(node_id), []).append(node_id)

def id_key(node_id):
    try:
        return (0, int(node_id))
    except ValueError:
        return (1, node_id)


for members in components.values():
    component_id = min(members, key=id_key)
    uri = f"www.example.com/person/{component_id}"

    for node_id in members:
        node_by_id[node_id]["data"]["uri"] = uri

edges = [item for item in data if item.get("group") == "edges"]

formatted_data = {
    "nodes": [{"data": item["data"]} for item in nodes],
    "edges": [{"data": item["data"]} for item in edges],
}

output_path = Path("../data/graph_output.json")
output_path.write_text(
    json.dumps(formatted_data, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)