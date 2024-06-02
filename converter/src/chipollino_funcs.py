import os
import subprocess
import re
from converter.models import TemporaryFile
from converter.src import tex_parser
import chipollino_web.env as env


def run_interpreter(text, session_key="0"):
    with open(f'Chipollino/{session_key}test.txt', 'w', encoding='utf-8') as f:
        f.write(text)
    try:
        os.chdir('Chipollino')
        subprocess.run(f'{env.CHIPOLLINO_BINARY} {session_key}test.txt {session_key}', check=True, shell=True)
        os.chdir('../')
    # except subprocess.CalledProcessError:
    except Exception:
        os.chdir('../')
        return None
    with open(f"Chipollino/resources/{session_key}report.tex", 'r', encoding='utf-8') as tex_file:
        tex_content = tex_file.read()
    return tex_content

def get_pdf(session_key="0"):
    file_path = f'Chipollino/{session_key}rendered_report.pdf'
    file_in_db, _ = TemporaryFile.objects.get_or_create(path=file_path, session_key=session_key)
    file_in_db.save()

    files = os.listdir('Chipollino')
    del_files = [f for f in files if f.startswith(session_key) and f != f'{session_key}rendered_report.pdf']
    for file in del_files:
        os.remove('Chipollino/' + file)
    
    if os.path.exists(file_path):
        with open(file_path, 'rb') as pdf_file:
            return pdf_file.read()
    else:
        return None

def parse_tex(text, session_key = "0"):
    res = tex_parser.parse_tex(text, session_key)
    os.remove(f"Chipollino/resources/{session_key}report.tex")
    os.remove(f"Chipollino/resources/{session_key}rendered_report.tex")
    return res

def create_svg(text, session_key="0"):
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
        os.chdir(folder_name)
        file_name = f'{session_key}_svg'
        with open(f'{file_name}.tex', 'w', encoding='utf-8') as f:
            f.write(tex_str)
        print('rendering graph image..')
        subprocess.run(f'latex {file_name}.tex', check=True, shell=True, stdout=subprocess.PIPE)
        subprocess.run(f'dvisvgm --no-fonts {file_name}.dvi {file_name}.svg', check=True, shell=True)
        with open(f'{file_name}.svg', 'r', encoding='utf-8') as svg_file:
            svg_str = svg_file.read()
            svg_str = re.sub(r"width='[^']*' height='[^']*'" , "width='100%'' height='100%'", svg_str)
        
        files = os.listdir()
        del_files = [f for f in files if f.startswith(f"{file_name}")]
        for file in del_files:
            os.remove(file)

        os.chdir('../')
    except subprocess.CalledProcessError:
        os.chdir('../')
        return None
    return svg_str

def get_random_object(type):
    try:
        os.chdir('Chipollino')
        res = subprocess.run(f'{env.CHIPOLLINO_GENERATOR_BINARY} {type}', stdout=subprocess.PIPE, check=True, shell=True)
        os.chdir('../')
        output = res.stdout.decode("utf-8")
        return output.replace('Input generator\n', '')
    # except subprocess.CalledProcessError:
    except Exception:
        os.chdir('../')
        return None
    