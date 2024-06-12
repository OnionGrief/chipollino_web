from converter.models import Graph, Table
import json
import re
from converter.src import tex_parser

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

def from_dsl(text):
    nodes, edges = {}, []
    text = text.strip()
    def parse_nodes(nlist):
        for line in [l for l in nlist.splitlines() if l and not l.isspace()]:
            line = line.strip()
            node_pattern = r'(?P<id>\S+)(?:\s+label\s*=\s*(?P<label>\S+))?(?:\s+(?P<final>final))?(?:\s+(?P<initial>initial_state))?\s*;'
            node_match = re.match(node_pattern, line)
    
            if not node_match:
                return None

            node_id = node_match.group('id')
            nodes[node_id] = {
                'id': node_id,
                'label': node_match.group('label') if node_match.group('label') else node_id,
                'is_double': bool(node_match.group('final')),
                'is_init': bool(node_match.group('initial'))
            }
    def add_edge(source, target, label):
        edges.append({"source": source, "target": target, "label": label})
        for n in [source, target]:
            if n not in nodes:
                nodes[n] = {"id": n, "label": n, "is_double": False, "is_init": False}

    if text.startswith("NFA"):
        pattern = re.compile(r'NFA(.*)\.\.\.(.*)$', re.DOTALL)
        nlist, elist = pattern.match(text).groups()
        parse_nodes(nlist)
        for line in [l for l in elist.splitlines() if l and not l.isspace()]:
            add_edge(*line.strip().split()[:-1])
    elif text.startswith("MFA"):
        pattern = re.compile(r'MFA(.*)\.\.\.(.*)$', re.DOTALL)
        nlist, elist = pattern.match(text).groups()
        parse_nodes(nlist)
        for line in [l for l in elist.splitlines() if l and not l.isspace()]:
            edge_pattern = r'(?P<source>\S+)\s+(?P<target>\S+)\s+(?P<label>.*\S)\s*;'
            edge_match = re.match(edge_pattern, line)
            add_edge(edge_match.group('source'), edge_match.group('target'), edge_match.group('label'))

    return Graph(nodes=nodes.values(), edges=edges)


def from_csv(text):
    columns, data = [], []
    lines = text.splitlines()
    for cell in lines[0].split(',')[1:]:
        columns.append(tex_parser.derender_regexpstr(cell))
    for r in lines[1:]:
        r = [tex_parser.derender_regexpstr(cell) for cell in r.split(',')]
        row_data = []
        for cell in r[1:]:
            row_data.append(cell)
        data.append({"first": r[0], "data": row_data})
    return Table(columns, data)