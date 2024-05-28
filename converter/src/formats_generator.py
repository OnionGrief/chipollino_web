from converter.models import Graph

def to_dsl(Graph):
    return ""

def to_dot(Graph):
    res = "digraph {\n\trankdir = LR\n\tnode [shape=circle]\n\tdummy [label = \"\", shape = none]\n"
    for state in Graph.nodes:
        res += f'\t{state["id"]} [label="{state["label"]}"{", shape=doublecircle" if state["is_double"] else ""}]\n'
        if state["is_init"]:
            res+=f'\tdummy -> {state["id"]}\n'
    for edge in Graph.edges:
        res += f'\t{edge["source"]} -> {edge["target"]} [label="{edge["label"]}"]\n'
    return res + "}"