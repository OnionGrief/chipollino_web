import re
import latex2mathml.converter

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

def create_tag(tag, text):
    return f'<{tag}>{text}</{tag}>'

def tex_parse(text):
    res = []

    text = get_content(text, '\maketitle', '\end{document}')

    text = re.sub(r"(?<!\\)%.*\n", "\n", text)
    text = re.sub(r"\\\\", "\n", text)
    text = re.sub(r"(?<!\\)\\ ", " ", text)
    text = re.sub(r"\\begin{frame}.*\n", "", text)
    text = re.sub(r"\\end{frame}\n", "", text)

    lines = text.splitlines()
    for line in lines:
        if not line.isspace() and line:
            if re.search(r"\\section{.*}", line):
                res.append(create_tag('h3', re.findall(r"\\section{(.*)}", line)[0] + ':'))
            else:
                print(repr(line))
                line = apply_mathml(line)
                res.append(create_tag('p', line))

    return res