import re
import latex2mathml.converter
from converter.models import Graph
from converter.src import chipollino_funcs, formats_generator
import graphviz

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
    text = derender_regexpstr(text)
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

def dot_to_svg(dot_source):
    svg_txt = graphviz.Source(dot_source).pipe(format='svg').decode('utf-8')
    return re.sub(r'width="[^"]*" height="[^"]*"' , 'width="100%" height="100%"', svg_txt)

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

def parse_tex(text, object_list, session_key = "0"):
    formats = []

    text = get_content(text, '\maketitle', '\end{document}')

    text = re.sub(r"(?<!\\)\\ ", " ", text)
    text = text.replace("\\\\", "\\\\\n")
    text = re.sub(r"(?<!\\)(?<!%)%[^%].*\n", "\n", text)
    text = re.sub(r"\\begin{frame}.*\n", "", text)
    text = re.sub(r"\\end{frame}.*\n", "", text)

    lines = [l for l in text.splitlines() if l and not l.isspace()]
    i = 0
    def get_content_until(end_mark, i):
        line = lines[i]
        graph_tex = ""
        while end_mark not in line and i < len(lines):
            graph_tex += line + '\n'
            i += 1
            line = lines[i]
        graph_tex += line
        return graph_tex, i
    while i < len(lines):
        line = lines[i].strip()
        if re.search(r"\\section{.*}", line):
            formats.append({'type': 'section', 'res': create_tag('h3', re.findall(r"\\section{(.*)}", line)[0] + ':')})
        elif "\\begin{tikzpicture}" in line:
            if "\\datavisualization" in lines[i+1]:
                plot_tex, i = get_content_until("\\end{tikzpicture}", i)
                svg_plot = chipollino_funcs.create_tex_svg(plot_tex, session_key=session_key)
                formats.append({'type': 'plot', 'res': svg_plot})
            else:
                graph_tex, i = get_content_until("\\end{tikzpicture}", i)
                svg_graph = chipollino_funcs.create_tex_svg(graph_tex, session_key=session_key)
                formats.append({'type': 'automaton', 'res': {'formats': [{'name': 'LaTeX', 'txt': graph_tex}], 'svg': svg_graph}})
        elif "$\\begin{array}" in line:
            table_tex, i = get_content_until("\end{array}$", i)
            svg_table = chipollino_funcs.create_tex_svg(table_tex, session_key=session_key)
            formats.append({'type': 'table', 'res': svg_table})
        elif re.search(r"%%.*\d+\.txt", line):
            if "\\begin{tikzpicture}" in lines[i+1]:
                graph_path = re.match(r"%%(.*\d+\.txt)", line).group(1)
                i += 1
                graph_tex, i = get_content_until("\\end{tikzpicture}", i)
                # graph = parse_tikz(graph_tex)
                graph = formats_generator.from_dsl(object_list[graph_path])
                dot_source = formats_generator.to_dot(graph)
                
                format_list = [{'name': 'DSL', 'txt': object_list[graph_path]}]
                format_list.append({'name': 'DOT', 'txt': formats_generator.to_dot(graph)})
                format_list.append({'name': 'LaTeX', 'txt': graph_tex})
                format_list.append({'name': 'JSON', 'txt': formats_generator.to_json(graph)})
                svg_graph = dot_to_svg(dot_source)
                formats.append({'type': 'automaton', 'res': {'formats': format_list, 'svg': svg_graph}})
            elif "$\\begin{array}" in lines[i+1]:
                table_path = re.match(r"%%(.*\d+\.txt)", line).group(1)
                i += 1
                table_tex, i = get_content_until("\end{array}$", i)
                svg_table = chipollino_funcs.create_tex_svg(table_tex, session_key=session_key)
                formats.append({'type': 'table', 'res': svg_table})
                formats.append({'type': 'text', 'res': create_tag('pre', object_list[table_path])})
        else:
            line = line.replace("\\\\", " ")
            line = apply_mathml(line)
            formats.append({'type': 'text', 'res': create_tag('p', line)})
        i += 1
    return formats