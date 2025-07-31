import networkx as nx
import json

def write_hif(G: nx.MultiDiGraph, path):
    incidences = []
    edges = []
    nodes = []
    for u, v, k in G.edges(keys=True):
        if k == 0:
            incidence = {"direction": "head", "edge": u, "node": v, "attrs": {"key": k}}
        else:
            incidence = {"direction": "tail", "edge": v, "node": u, "attrs": {"key": k}}
        incidences.append(incidence)
    for u, d in G.nodes(data=True):
        if len(d) > 1:
            a = d.copy()
            del a["bipartite"]
            if d["bipartite"] == 1:
                edge = {"edge": u, "attrs": a}
                edges.append(edge)
            else:
                node = {"node": u, "attrs": a}
                nodes.append(node)
    data = {"incidences": incidences, "edges": edges, "nodes": nodes}
    with open(path, "w") as file:
        file.write(json.dumps(data, indent=2))

def add_incidence(G: nx.MultiDiGraph, incidence):
    attrs = incidence.get("attrs", {})
    edge_id = incidence["edge"], 1
    node_id = incidence["node"], 0
    if "weight" in incidence:
        attrs["weight"] = incidence["weight"]
    if "direction" in incidence:
        attrs["direction"] = incidence["direction"]
    G.add_node(edge_id, bipartite=1)
    G.add_node(node_id, bipartite=0)
    if incidence.get("direction") == "tail":
        G.add_edge(node_id, edge_id, **attrs)
    else:
        G.add_edge(edge_id, node_id, **attrs)

def add_edge(G: nx.MultiDiGraph, edge):
    attrs = edge.get("attrs", {})
    edge_id = edge["edge"], 1
    if "weight" in edge:
        attrs["weight"] = edge["weight"]
    if not G.has_node(edge_id):
        G.add_node(edge_id, bipartite=1)
    for attr_key, attr_value in attrs.items():
        G.nodes[edge_id][attr_key] = attr_value

def add_node(G: nx.MultiDiGraph, node):
    attrs = node.get("attrs", {})
    node_id = node["node"], 0
    if "weight" in node:
        attrs["weight"] = node["weight"]
    if not G.has_node(node_id):
        G.add_node(node_id, bipartite=0)
    for attr_key, attr_value in attrs.items():
        G.nodes[node_id][attr_key] = attr_value

def read_hif(path):
    with open(path) as file:
        data = json.loads(file.read())
    return read_hif_data(data)

def read_hif_data(data):
    G_attrs = data.get("metadata", {})
    if "network-type" in data:
        G_attrs["network-type"] = data["network-type"]
    G = nx.MultiDiGraph(**G_attrs)
    for i in data["incidences"]:
        add_incidence(G, i)
    for e in data.get("edges", []):
        add_edge(G, e)
    for n in data.get("nodes", []):
        add_node(G, n)
    return G
