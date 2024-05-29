import re
import latex2mathml.converter
from converter.models import Graph
from converter.src import formats_generator

# получить часть файла от begin до end_mark
def get_content(text, begin, end_mark="}"):
    insert_index = text.find(begin)
    if insert_index == -1:
        print("not found " + begin)
        return
    brace_index = text.find(end_mark, insert_index)
    return text[insert_index+len(begin):brace_index]

# получить часть файла от begin + { блок между скобками }
def get_content_in_brackets(text, begin):
    insert_index = text.find(begin)
    insert_index = text.find('{', insert_index)
    if insert_index == -1:
        print("not found " + begin)
        return
    i = insert_index
    count = 1
    for s in text[insert_index+1:]:
        count += 1 if s == '{' else -1 if s == '}' else 0
        i+=1
        if count == 0:
            break

    return text[insert_index+len(begin):i]

# заменяет $tex math mode$ на math ml (html)
def apply_mathml(text):
    def replace_substring(match):
        return latex2mathml.converter.convert(match.group(1))
    return re.sub(r'\$([^\$]*)\$', replace_substring, text)

# заменяет $\regexpstr{..}$ на ..
def del_regexpstr(text):
    text = re.sub(r'\\pgfsetfillopacity{[^}]*}', "", text)
    def replace_substring(match):
        return '$' + match.group(1) + '$'
    return re.sub(r'\$\\regexpstr{([^\$]*) }\$', replace_substring, text)

def del_empt(text):
    return re.sub(r'\\empt', 'ε', text)

def create_tag(tag, text):
    return f'<{tag}>{text}</{tag}>'

def parse_tikz(text):
    text = del_empt(del_regexpstr(text))
    lines = text.split("\n")
    nodes, edges = {}, []
    dummy = ""
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("\\node"):
            node_match = re.match(r"\\node \(([^\)]*)\)[^\[]*\[([^\]]*)\] {\$([^\$]*)\$};", line)
            id, style, label = node_match.groups()
            is_double, is_dummy = False, False
            if "double" in style:
                is_double = True
            if "draw=none" in style:
                is_dummy = True
                dummy = id
            else:
                nodes[id] = {"id": id, "label": label, "is_double": is_double, "is_init": False}
        elif line.startswith("\\draw [->, thick]"):
            edge_match = re.match(r"\\draw \[->, thick\] \(([^\)]*)\).*\(([^\(]*)\);", line)
            source, target = edge_match.groups()
            line2 = lines[i+1].strip()
            label = ""
            if line2.startswith("\\draw ("):
                label_match = re.match(r"\\draw .*{\$([^\$]*)\$};", line2)
                label = label_match.group(1)
                i += 1
            if source == dummy:
                nodes[target]["is_init"] = True
            else:
                edges.append({"source": source, "target": target, "label": label})
        i += 1

    return Graph(nodes=nodes.values(), edges=edges)

def parse_tex(text):
    res = []

    text = get_content(text, '\maketitle', '\end{document}')

    text = re.sub(r"(?<!\\)%.*\n", "\n", text)
    text = re.sub(r"\\\\", "\n", text)
    text = re.sub(r"(?<!\\)\\ ", " ", text)
    text = re.sub(r"\\begin{frame}.*\n", "", text)
    text = re.sub(r"\\end{frame}\n", "", text)

    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.isspace() and line:
            if re.search(r"\\section{.*}", line):
                res.append({'type': 'section', 'res': create_tag('h3', re.findall(r"\\section{(.*)}", line)[0] + ':')})
            elif "\\begin{tikzpicture}" in line:
                graph_tex = line
                while "\\end{tikzpicture}" not in line and i < len(lines):
                    i += 1
                    line = lines[i]
                    graph_tex += '\n' + line
                format_list = [{'name': 'LaTeX', 'txt': graph_tex}]
                graph = parse_tikz(graph_tex)
                format_list.append({'name': 'DOT', 'txt': formats_generator.to_dot(graph)})
                format_list.append({'name': 'DSL', 'txt': formats_generator.to_dsl(graph)})
                res.append({'type': 'automaton', 'res': format_list})
            else:
                print(repr(line))
                line = apply_mathml(line)
                res.append({'type': 'text', 'res': create_tag('p', line)})
        i += 1

    return res