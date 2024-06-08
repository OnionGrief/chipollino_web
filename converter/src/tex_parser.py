import re
import latex2mathml.converter
from converter.models import Graph
from converter.src import chipollino_funcs, formats_generator

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
    begin_index = text.find(begin)
    lbracket_index = text.find('{', begin_index)
    if lbracket_index == -1:
        print("not found " + begin)
        return
    i = lbracket_index
    count = 1
    for s in text[lbracket_index+1:]:
        count += 1 if s == '{' else -1 if s == '}' else 0
        i+=1
        if count == 0:
            break

    return text[begin_index:i+1], text[lbracket_index+1:i]

# заменяет $tex math mode$ на math ml (html)
def apply_mathml(text):
    def replace_substring(match):
        return latex2mathml.converter.convert(match.group(1))
    return re.sub(r'\$([^\$]*)\$', replace_substring, text)


def remove_substring_until_none(string, substring):
    while substring in string:
        str1, str2 = get_content_in_brackets(string, substring)
        string = string.replace(str1, str2)
    return string

def derender_regexpstr(text):
    text = re.sub(r'\\empt', 'ε', text)
    text = re.sub(r'\\hspace\*?{[^}]*}', "", text)
    text = re.sub(r'\\pgfsetfillopacity{[^}]*}{', "-pgfsetfillopacity{", text)
    text = re.sub(r'\\pgfsetfillopacity{[^}]*}', "", text)
    text = remove_substring_until_none(text, "-pgfsetfillopacity")
    text = remove_substring_until_none(text, "\\regexpstr")
    # def replace_substring(match):
    #     return '$' + match.group(1) + '$'
    # return re.sub(r'\$\\regexpstr{([^\$]*) }\$', replace_substring, text)
    return text

def create_tag(tag, text):
    return f'<{tag}>{text}</{tag}>'

def parse_tikz(text):
    text = derender_regexpstr(text)
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

def parse_tex(text, session_key = "0"):
    formats = []
    svg_graph = ""

    text = get_content(text, '\maketitle', '\end{document}')

    text = re.sub(r"(?<!\\)\\ ", " ", text)
    text = text.replace("\\\\", "\n")
    text = re.sub(r"(?<!\\)%.*\n", "\n", text)
    text = re.sub(r"\\begin{frame}.*\n", "", text)
    text = re.sub(r"\\end{frame}\n", "", text)

    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.isspace() and line:
            if re.search(r"\\section{.*}", line):
                formats.append({'type': 'section', 'res': create_tag('h3', re.findall(r"\\section{(.*)}", line)[0] + ':')})
            elif "\\begin{tikzpicture}" in line:
                if "\\datavisualization" in lines[i+1]:
                    plot_tex = line
                    while "\\end{tikzpicture}" not in line and i < len(lines):
                        i += 1
                        line = lines[i]
                        plot_tex += '\n' + line
                    
                    i += 1
                    line = lines[i]
                    svg_plot = chipollino_funcs.create_svg(plot_tex, session_key=session_key)
                    formats.append({'type': 'plot', 'res': svg_plot})
                else:
                    graph_tex = line
                    while "\\end{tikzpicture}" not in line and i < len(lines):
                        i += 1
                        line = lines[i]
                        graph_tex += '\n' + line
                    i+=1
                    graph_tex += lines[i]
                    format_list = [{'name': 'LaTeX', 'txt': graph_tex}]
                    graph = parse_tikz(graph_tex)
                    format_list.append({'name': 'DOT', 'txt': formats_generator.to_dot(graph)})
                    format_list.append({'name': 'DSL', 'txt': formats_generator.to_dsl(graph)})
                    format_list.append({'name': 'JSON', 'txt': formats_generator.to_json(graph)})
                    svg_graph = chipollino_funcs.create_svg(graph_tex, session_key=session_key)
                    formats.append({'type': 'automaton', 'res': {'formats': format_list, 'svg': svg_graph}})
            elif "$\\begin{array}" in line:
                table_tex = line
                while "\end{array}$" not in line and i < len(lines):
                    i += 1
                    line = lines[i]
                    table_tex += '\n' + line
                i+=1
                table_tex += lines[i]
                svg_table = chipollino_funcs.create_svg(table_tex, session_key=session_key)
                formats.append({'type': 'table', 'res': svg_table})
            else:
                line = re.sub(r"\\\\", "\n", line)
                line = apply_mathml(line)
                formats.append({'type': 'text', 'res': create_tag('p', line)})
        i += 1

    return formats