from converter.models import Graph
import json

def to_json(graph: Graph):
    return json.dumps({"nodes": list(graph.nodes), "edges": graph.edges}, indent=2)

def to_dsl(graph: Graph):
    res = "NFA\n"
    for state in graph.nodes:
        res += f'{state["id"]} label={state["label"]}{" final" if state["is_double"] else ""}{" initial_state" if state["is_init"] else ""} ;\n'
    res += "...\n"
    for edge in graph.edges:
        res += edge["source"] + ' ' + edge["target"] + ' ' + edge["label"] + ' ;\n'
    res = res.replace('ε', 'eps')
    return res

def to_dot(graph: Graph):
    res = "digraph {\n\trankdir = LR\n\tnode [shape=circle]\n\tdummy [label = \"\", shape = none]\n"
    for state in graph.nodes:
        res += f'\t{state["id"]} [label="{state["label"]}"{", shape=doublecircle" if state["is_double"] else ""}]\n'
        if state["is_init"]:
            res+=f'\tdummy -> {state["id"]}\n'
    for edge in graph.edges:
        res += f'\t{edge["source"]} -> {edge["target"]} [label="{edge["label"]}"]\n'
    return res + "}"