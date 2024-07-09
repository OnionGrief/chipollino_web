from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
import os
import json
import yaml
from .models import TemporaryFile, Graph, GraphDB
from converter.src import chipollino_funcs, formats_generator
from django.conf import settings

def index(request):
    if not request.session.session_key:
        request.session.create()

    format_list = formats_generator.get_format_list()
    graphs = GraphDB.objects.filter(session_key=request.session.session_key)
    graphs = [g.to_Graph() for g in graphs]
    return render(request, 'converter/index.html', 
                {'format_list': format_list, 'graph_list': graphs, 'func_list': load_yaml_data()["functions"]})

def help_page(request):
    return render(request, 'converter/help.html')


def run_interpreter(request):
    session_key = request.session.session_key
    if request.method == 'POST':
        try:
            text = request.POST['input-txt']
            prev_text = text
            for g in GraphDB.objects.filter(session_key=session_key):
                g_name = g.name
                user_path = 'Chipollino/' + session_key
                if not os.path.exists(user_path):
                    os.mkdir(user_path)
                with open(f'{user_path}/{g_name}.txt', 'w', encoding='utf-8') as f:
                    f.write(formats_generator.to_dsl(g.to_Graph()))
                text = f'{g_name} = "{session_key}/{g_name}.txt"\n' + text

            running_res, rendered_tex, ok, graph_list = chipollino_funcs.run_interpreter(text, session_key)
            request.session['rendered_tex'] = rendered_tex
            if ok:
                tex_file = running_res
                result_list = chipollino_funcs.parse_tex(tex_file, graph_list, session_key = session_key)
                return render(request, 'converter/result.html', {'success': True, 'test': prev_text, 'texresult': tex_file, 'rendered_tex': repr(rendered_tex), 'result_list': result_list})
            else:
                if running_res:
                    return render(request, 'converter/result.html', {'test': running_res})
                else:
                    return render(request, 'converter/result.html', {'test': "Converter error"})
        except Exception:
            return render(request, 'converter/result.html', {'test': "Converter error"})


def get_pdf(request):
    pdf_file = chipollino_funcs.get_pdf(request.session.session_key, request.session["rendered_tex"])
    if pdf_file:
        return HttpResponse(pdf_file, content_type='application/pdf')
    else:
        return HttpResponse("PDF file not found", status=404)


def tex_view(request):
    if request.method == 'POST':
        try:
            tex_content = json.loads(request.body).get('tex_content', '')
            svg_content = chipollino_funcs.create_tex_svg(tex_content, request.session.session_key)
            if svg_content:
                    return HttpResponse(svg_content, content_type='image/svg+xml')
            else:
                return HttpResponse("Can't create svg from TeX", status=404)
        except Exception:
            return HttpResponse("Can't load tikz_view", status=404)


def get_graph(request, graph_id):
    if request.method == 'GET':
        g = get_object_or_404(GraphDB, id=graph_id).to_Graph()
        res = formats_generator.to_dsl(g)
        format_list = formats_generator.map_format_list()
        return JsonResponse({'text': res, 'format': 'DSL', 'editable': format_list['DSL']['editable'], 'svg': formats_generator.svg_graphviz(g)})

def get_graph_format(request, graph_id, format_name):
    if request.method == 'GET':
        try:
            g_db = get_object_or_404(GraphDB, id=graph_id)
            g = g_db.to_Graph()
            format_list = formats_generator.map_format_list()
            res = format_list[format_name]['to'](g)
            return JsonResponse({'text': res, 'editable': format_list[format_name]['editable'], 
                                'svg': formats_generator.svg_graphviz(g)})
        except Exception:
            return HttpResponse("Can't get format " + format_name, status=404)

def convert_graph_format(request, format_name):
    if request.method == 'POST':
        try:
            req_body = json.loads(request.body)
            from_format = req_body.get('format', '')
            graph_content = req_body.get('content', '')
            format_list = formats_generator.map_format_list()
            g = format_list[from_format]['from'](graph_content)
            res = format_list[format_name]['to'](g)
            return JsonResponse({'text': res, 'svg': formats_generator.svg_graphviz(g)})
        except Exception:
            return HttpResponse("Can't get format " + format_name, status=404)  

def get_svg_graph(request):
    if request.method == 'POST':
        try:
            req_body = json.loads(request.body)
            graph_format = req_body.get('format', '')
            graph_content = req_body.get('content', '')
            format_list = formats_generator.map_format_list()
            assert(format_list[graph_format]['editable'])
            g = format_list[graph_format]['from'](graph_content)
            return HttpResponse(formats_generator.svg_graphviz(g), content_type='image/svg+xml')
        except Exception:
            return HttpResponse("None")

def add_graph(request):
    if request.method == 'POST':
        try:
            req_body = json.loads(request.body)
            graph_name = req_body.get('name', '0')
            dsl_content = req_body.get('dsl_content', '')
            GraphDB.objects.filter(session_key=request.session.session_key, name=graph_name).delete()
            g = formats_generator.from_dsl(dsl_content).to_GraphDB()
            g.session_key = request.session.session_key
            g.name = graph_name
            g.save()
            return HttpResponse(f"Saved graph {graph_name}")
        except Exception:
            return HttpResponse("Can't save graph", status=404)

def create_graph(request):
    if request.method == 'POST':
        try:
            graph_name = json.loads(request.body).get('name', '0')
            if len(GraphDB.objects.filter(session_key=request.session.session_key, name=graph_name)) > 0:
                return HttpResponse(f"Name {graph_name} already exists", status=404)
            g = Graph([{"id": 0, "label": "S", "is_init": True, "is_double": False}], [], graph_name).to_GraphDB()
            g.session_key = request.session.session_key
            g.save()
            return JsonResponse({"id": g.id})
        except Exception:
            return HttpResponse("Can't create graph", status=404)

def save_graph(request, graph_id):
    if request.method == 'POST':
        try:
            req_body = json.loads(request.body)
            graph_format = req_body.get('format', '')
            format_list = formats_generator.map_format_list()
            assert(format_list[graph_format]['editable'])
            graph_content = req_body.get('content', '')
            g_db = get_object_or_404(GraphDB, id=graph_id)
            g = format_list[graph_format]['from'](graph_content)
            g_db.update_from(g)
            g_db.save()
            return HttpResponse(f"Saved graph {g_db.name}")
        except Exception:
            return HttpResponse("Can't save graph", status=404)

def delete_graph(request, graph_id):
    if request.method == 'GET':
        g = get_object_or_404(GraphDB, pk=graph_id)
        g_name = g.name
        g.delete()
        return HttpResponse(f"Graph {g_name} deleted")

        
def get_random_object(request, object_type):
    if request.method == 'GET':
        res = chipollino_funcs.get_random_object(object_type)
        if object_type in ['MFA', 'NFA']:
            res = f"get{object_type} "
        return HttpResponse(res)



def load_yaml_data():
    yaml_file_path = settings.CONFIG_DIR / 'config.yaml'
    with open(yaml_file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data


from django.contrib.sessions.models import Session
from django.utils import timezone
from datetime import datetime, timedelta

def is_session_active(session_key):
    try:
        session = Session.objects.get(session_key=session_key)
        if session.expire_date > timezone.now():
            return True
        else:
            session.delete()
    except Session.DoesNotExist:
        return False
    return False

def delete_files(request):
    old_files = TemporaryFile.objects.filter(created_at__lt = datetime.utcnow() - timedelta(days=1))
    count = 0
    for file in old_files:
        if not is_session_active(file.session_key):
            if os.path.exists(file.path):
                os.remove(file.path)
                count += 1
            file.delete()
    return HttpResponse(f"deleted {count} files")

def delete_graphs(request):
    sessions = GraphDB.objects.values_list('session_key', flat=True).distinct()
    count = 0
    for s in sessions:
        if not is_session_active(s):
            deleted_count, _ = GraphDB.objects.filter(session_key=s).delete()
            count += deleted_count
    return HttpResponse(f"deleted {count} graphs")

    
