from converter.models import Graph, Table
import json
import re
from converter.src import tex_parser
import graphviz

# graph formats

# def get_format_funcs():
#     return {}
def get_format_list():
    return [{'name': 'DSL', 'editable': True, 'to': to_dsl, 'from': from_dsl}, 
            {'name': 'DOT', 'editable': False, 'to': to_dot},
            {'name': 'JSON', 'editable': True, 'to': to_json, 'from': from_json}]
def map_format_list():
    formats = {}
    for f in get_format_list():
        # f['to'] = get_format_funcs()[f['name']]
        formats[f['name']] = f
    return formats

def dot_to_svg(dot_source):
    svg_txt = graphviz.Source(dot_source).pipe(format='svg').decode('utf-8')
    return re.sub(r'width="[^"]*" height="[^"]*"' , 'width="100%"', svg_txt)
def svg_graphviz(g: Graph):
    return dot_to_svg(to_dot(g))


def to_json(graph: Graph):
    json_nodes = [{"data": { "id": 'dummy', "label": ''}, "classes": 'dummy'}]
    json_edges = []
    for n in graph.nodes:
        json_node = {"data": {"id": n["id"], "label": n["label"]}}
        if n["is_double"]:
            json_node["classes"] = 'doublecircle'
        if n["is_init"]:
            json_edges.append({"data": {"source": 'dummy', "target": n["id"], "label": ''}})
        json_nodes.append(json_node)
    for e in graph.edges:
        json_edges.append({"data": {"source": e["source"], "target": e["target"], "label": e["label"]}})

    return json.dumps({"nodes": json_nodes, "edges": json_edges}, indent=2, ensure_ascii=False)

def to_dsl(graph: Graph):
    res = "NFA\n"
    for state in graph.nodes:
        res += f'{state["id"]}{" final" if state["is_double"] else ""}{" initial_state" if state["is_init"] else ""} label={state["label"]} ;\n'
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

def to_gdf(graph: Graph):
    res = "nodedef> name VARCHAR,label VARCHAR\n"
    for state in graph.nodes:
        res += f'{state["id"]},"{state["label"]}"\n'
    res += "edgedef> node1,node2,label VARCHAR,directed BOOLEAN"
    for edge in graph.edges:
        res += f'{edge["source"]},{edge["target"]},"{edge["label"]}",true\n'
    return res

def to_gml(graph: Graph):
    res = "["
    for state in graph.nodes:
        res += f"""
    node
    [
        id {state["id"]}
        label "{state["label"]}"
    ]"""
    for edge in graph.edges:
        res += f"""
    edge
    [
        source {edge["source"]}
        target {edge["target"]}
        label "{edge["label"]}"
    ]"""
    return res + '\n]'

def to_graphml(graph: Graph):
    res = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
    <key attr.name="label" attr.type="string" for="node" id="label"/>
    <key attr.name="Edge Label" attr.type="string" for="edge" id="edgelabel"/>
    <graph edgedefault="directed">"""
    for state in graph.nodes:
        res += f"""
        <node id="{state["id"]}">
            <data key="label">{state["label"]}</data>
        </node>"""
    edge_num = 0
    for edge in graph.edges:
        edge_num += 1
        res += f"""
        <edge id="e{edge_num}" source="{edge["source"]}" target="{edge["target"]}">
            <data key="edgelabel">{edge["label"]}</data>
        </edge>"""
    res += """
    </graph>
</graphml>"""
    return res

def to_gexf(graph: Graph):
    res = """<?xml version='1.0' encoding='UTF-8'?>
<gexf xmlns="http://gexf.net/1.2" version="1.2">
  <graph defaultedgetype="directed" mode="static">
    <nodes>"""
    for state in graph.nodes:
        res += f"""
      <node id="{state["id"]}" label="{state["label"]}"/>"""
    res += """
    </nodes>
    <edges>"""
    edge_num = 0
    for edge in graph.edges:
        edge_num += 1
        res += f"""
      <edge id="e{edge_num}" source="{edge["source"]}" target="{edge["target"]}" label="{edge["label"]}"/>"""
    res += """
    </edges>
  </graph>
</gexf>"""
    return res


def from_dsl(text):
    nodes, edges = {}, []
    text = text.strip()
    text = text.replace('eps','ε')
    type = "NFA"
    def parse_nodes(nlist):
        for line in [l for l in nlist.splitlines() if l and not l.isspace()]:
            line = line.strip()
            node_pattern = r'(?P<id>\S+)(?:\s+(?P<final>final))?(?:\s+(?P<initial>initial_state))?(?:\s+label\s*=\s*(?P<label>.*))?\s*;'
            node_match = re.match(node_pattern, line)

            # if not node_match:
            #     return None

            node_id = node_match.group('id')
            nodes[node_id] = {
                'id': node_id,
                'label': node_match.group('label').strip() if node_match.group('label') else node_id,
                'is_double': bool(node_match.group('final')),
                'is_init': bool(node_match.group('initial'))
            }
    def add_edge(source, target, label):
        edges.append({"source": source, "target": target, "label": label})
        for n in [source, target]:
            if n not in nodes:
                nodes[n] = {"id": n, "label": n, "is_double": False, "is_init": False}

    try:
        if text.startswith("NFA"):
            pattern = re.compile(r'NFA(.*)\.\.\.(.*)$', re.DOTALL)
            nlist, elist = pattern.match(text).groups()
            parse_nodes(nlist)
            for line in [l for l in elist.splitlines() if l and not l.isspace()]:
                add_edge(*line.strip().split()[:-1])
        else:
            assert text.startswith("MFA")
            type = "MFA"
            pattern = re.compile(r'MFA(.*)\.\.\.(.*)$', re.DOTALL)
            nlist, elist = pattern.match(text).groups()
            parse_nodes(nlist)
            for line in [l for l in elist.splitlines() if l and not l.isspace()]:
                edge_pattern = r'(?P<source>\S+)\s+(?P<target>\S+)\s+(?P<label>.*\S)\s*;'
                edge_match = re.match(edge_pattern, line)
                add_edge(edge_match.group('source'), edge_match.group('target'), edge_match.group('label'))
    except Exception:
        return None
    return Graph(nodes=nodes.values(), edges=edges, type=type)

def from_json(json_graph):
    g_data = json.loads(json_graph)
    nodes, edges = {}, []
    dummy = "dummy"

    for n_data in g_data.nodes:
        n = n_data["data"]
        nodes[n["id"]] = {"id": n["id"], "label": n["label"], "is_double": False, "is_init": False}
        if 'classes' in n_data:
            if n_data["classes"] == 'doublecircle':
                nodes[id]["is_double"] = True
        if id == dummy:
            assert(n_data["classes"] == 'dummy')
    assert(dummy in nodes)
    nodes.pop(dummy)
    
    count_init = 0
    for e_data in g_data.edges:
        e = e_data["data"]
        edges.append({"source": e["source"], "target": e["target"], "label": e["label"]})
        if e["source"] == dummy:
            nodes[e["target"]]["is_init"] = True
            count_init += 1
    assert(count_init == 1)

    return Graph(nodes=nodes.values(), edges=edges)


# table formats

def from_csv(text):
    columns, rows = [], []
    lines = text.splitlines()
    for cell in lines[0].split(';')[1:]:
        columns.append(tex_parser.derender_regexpstr(cell))
    for r in lines[1:]:
        r = [tex_parser.derender_regexpstr(cell) for cell in r.split(';')]
        row_data = []
        for cell in r[1:]:
            row_data.append(cell)
        rows.append({"first": r[0], "data": row_data})
    return Table(columns, rows)

def to_md(t: Table):
    res, line = "|       |", "| ----- |"
    for c in t.columns:
        res += f" {c} |"
        line += " - |"
    res += '\n' + line
    for row in t.rows:
        res += f'\n| **{row["first"]}** |'
        for cell in row["data"]:
            res += f' {cell} |'
    return res

def to_asciidoc(t: Table):
    res, line = "|     ", '[cols="1'
    for c in t.columns:
        res += f"| *{c}* "
        line += ",1"
    res = line + '"]\n|===\n' + res
    for row in t.rows:
        res += f'\n| *{row["first"]}*'
        for cell in row["data"]:
            res += ' | ' + cell
    return res + "\n|==="

def table_to_json(t: Table):
    return json.dumps({"columns": t.columns, "rows": t.rows}, indent=2, ensure_ascii=False)