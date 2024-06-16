from django.shortcuts import render
from django.http import HttpResponse
import os
import json
from .models import TemporaryFile, Graph, GraphDB

def index(request):
    if not request.session.session_key:
        request.session.create()

    format_list = [{'name': 'DSL', 'editable': True}, {'name': 'DOT', 'editable': False}]
    graphs = GraphDB.objects.filter(session_key=request.session.session_key)
    graphs = [g.to_Graph() for g in graphs]
    return render(request, 'converter/index.html', {'format_list': format_list, 'graph_list': graphs})


from converter.src import chipollino_funcs, formats_generator

def run_interpreter(request):
    session_key = request.session.session_key
    if request.method == 'POST':
        text = request.POST['input-txt']
        running_res, rendered_tex, ok, graph_list = chipollino_funcs.run_interpreter(text, session_key)
        request.session['rendered_tex'] = rendered_tex
        if ok:
            tex_file = running_res
            result_list = chipollino_funcs.parse_tex(tex_file, graph_list, session_key = session_key)
            return render(request, 'converter/result.html', {'success': True, 'test': text, 'texresult': tex_file, 'result_list': result_list})
        else:
            if running_res:
                return render(request, 'converter/result.html', {'test': running_res})
            else:
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


def add_graph(request):
    if request.method == 'POST':
        try:
            req_body = json.loads(request.body)
            graph_name = req_body.get('name', '')
            dsl_content = req_body.get('dsl_content', '')
            GraphDB.objects.filter(session_key=request.session.session_key, name=graph_name).delete()
            print(graph_name)
            g = formats_generator.from_dsl(dsl_content).to_GraphDB()
            g.session_key = request.session.session_key
            g.name = graph_name
            g.save()
            return HttpResponse(f"Saved graph {graph_name}")
        except Exception:
            return HttpResponse("Can't save graph", status=404)

        
def get_random_object(request, object_type):
    if request.method == 'GET':
        res = chipollino_funcs.get_random_object(object_type)
        if object_type in ['MFA', 'NFA']:
            res = f"get{object_type} "
        return HttpResponse(res)


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
    sessions = Graph.objects.values_list('session_key', flat=True).distinct()
    count = 0
    for s in sessions:
        if not is_session_active(s):
            deleted_count, _ = Graph.objects.filter(session_key=s).delete()
            count += deleted_count
    return HttpResponse(f"deleted {count} graphs")

    
