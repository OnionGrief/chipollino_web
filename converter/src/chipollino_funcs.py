import os
import subprocess
import shutil
import re
from converter.models import TemporaryFile
from converter.src import tex_parser
import chipollino_web.env as env


def run_interpreter(text, session_key="0"):
    user_path = 'Chipollino/' + session_key
    if not os.path.exists(user_path):
        os.mkdir(user_path)
    with open(f'Chipollino/{session_key}/test.txt', 'w', encoding='utf-8') as f:
        f.write(text)
    try:
        subprocess.run(f"{env.CHIPOLLINO_BINARY} {session_key}/test.txt {session_key}", check=True, shell=True, capture_output=True, text=True, cwd='Chipollino')
    except subprocess.CalledProcessError as e:
        shutil.rmtree(user_path)
        return e.stderr, False, []
    except Exception:
        shutil.rmtree(user_path)
        return None, False, []
    with open(f"Chipollino/resources/{session_key}report.tex", 'r', encoding='utf-8') as tex_file:
        tex_content = tex_file.read()
    graphs = {}
    files = os.listdir(user_path)
    for file in files:
        if re.match(r'\d+.txt', file):
            with open(f"{user_path}/{file}", 'r', encoding='utf-8') as graph:
                graphs[f"{session_key}/{file}"] = graph.read()
    os.remove(f"Chipollino/resources/{session_key}report.tex")
    os.remove(f"Chipollino/resources/{session_key}rendered_report.tex")
    shutil.rmtree(user_path)
    return tex_content, True, graphs

def get_pdf(session_key="0"):
    file_path = f'Chipollino/{session_key}rendered_report.pdf'
    # file_in_db, _ = TemporaryFile.objects.get_or_create(path=file_path, session_key=session_key)
    # file_in_db.save()

    files = os.listdir('Chipollino')
    del_files = [f for f in files if f.startswith(session_key) and f != f'{session_key}rendered_report.pdf']
    for file in del_files:
        os.remove('Chipollino/' + file)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as pdf_file:
            pdf_binary = pdf_file.read()
        os.remove(file_path)
        return pdf_binary
    else:
        return None

def parse_tex(text, graph_list, session_key = "0"):
    res = tex_parser.parse_tex(text, graph_list, session_key)
    return res

def create_tex_svg(text, session_key="0"):
    svg_str = ""
    try:
        tex_str = ""
        with open("Chipollino/resources/template/head.tex", 'r', encoding='utf-8') as head_file:
            tex_str += head_file.read().replace('\\maketitle', '')
        tex_str = tex_str.replace('\\begin{document}', '\\usepackage[pdftex,active,tightpage]{preview}\n\\begin{document}')
        tex_str += '\\begin{preview}'
        tex_str += text
        tex_str += '\\end{preview}\n\\end{document}'

        folder_name = 'tmp'
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)
        file_name = f'{session_key}_svg'
        with open(f'{folder_name}/{file_name}.tex', 'w', encoding='utf-8') as f:
            f.write(tex_str)
        # print('rendering graph image..')
        subprocess.run(f'latex {file_name}.tex', check=True, shell=True, stdout=subprocess.PIPE, cwd=folder_name)
        subprocess.run(f'dvisvgm --no-fonts {file_name}.dvi {file_name}.svg', check=True, shell=True, capture_output=True,cwd=folder_name)
        
        with open(f'{folder_name}/{file_name}.svg', 'r', encoding='utf-8') as svg_file:
            svg_str = svg_file.read()
            svg_str = re.sub(r"width='[^']*' height='[^']*'" , "width='100%'' height='100%'", svg_str)
        
        files = os.listdir(folder_name)
        del_files = [f for f in files if f.startswith(f"{file_name}")]
        for file in del_files:
            file = os.path.join(folder_name, file)
            os.remove(file)
    except subprocess.CalledProcessError:
        return None
    return svg_str

def get_random_object(type):
    try:
        res = subprocess.run(f"{env.CHIPOLLINO_GENERATOR_BINARY} {type} false", stdout=subprocess.PIPE, check=True, shell=True, cwd='Chipollino')
        output = res.stdout.decode("utf-8")
        return re.sub(r'Input generator\s*', '', output)
    # except subprocess.CalledProcessError:
    except Exception:
        return None
    