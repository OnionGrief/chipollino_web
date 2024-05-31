from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.generic import ListView, DetailView
from django.http import HttpResponse, FileResponse
import os
from .models import TemporaryFile

def index(request):
    return render(request, 'converter/index.html')


from converter.src import chipollino_funcs, tex_parser

def generator(request):
    str1 = chipollino_funcs.getString()
    return render(request, 'converter/generator.html', {'smth': str1})

def get_random_regex(request):
    return HttpResponse(chipollino_funcs.getRegex())

def run_interpreter(request):
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    if request.method == 'POST':
        text = request.POST['input-txt']
        tex_file = chipollino_funcs.run_interpreter(text, session_key)
        if tex_file:
            result_list = chipollino_funcs.parse_tex(tex_file, session_key = session_key)
            return render(request, 'converter/result.html', {'success': True, 'test': text, 'texresult': tex_file, 'result_list': result_list})
        else:
            return render(request, 'converter/result.html', {'test': "Converter error"})

def pdf_view(request):
    pdf_file = chipollino_funcs.get_pdf(request.session.session_key)
    if pdf_file:
            return HttpResponse(pdf_file, content_type='application/pdf')
    else:
        return HttpResponse("PDF file not found", status=404)


from datetime import datetime, timedelta

def delete_files(request):
    old_files = TemporaryFile.objects.filter(created_at__lt = datetime.utcnow() - timedelta(days=1))
    count = len(old_files)
    for file in old_files:
        os.remove(file.path)
    old_files.delete()
    return HttpResponse(f"deleted {count} files")

    
