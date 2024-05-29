from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.generic import ListView, DetailView
from django.http import HttpResponse, FileResponse
import os

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
        with open('Chipollino/test.txt', 'w') as f:
            f.write(text)
        tex_file = chipollino_funcs.run_interpreter("")
        if tex_file:
            result_list = tex_parser.parse_tex(tex_file, session_key = session_key)
            return render(request, 'converter/result.html', {'success': True, 'test': text, 'texresult': tex_file, 'result_list': result_list})
        else:
            return render(request, 'converter/result.html', {'test': "Converter error"})

def pdf_view(request):
    file_path = 'Chipollino/rendered_report.pdf'
    if os.path.exists(file_path):
        with open(file_path, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            # response.close()
            # os.remove(file_path)
            return response
    else:
        return HttpResponse("PDF file not found", status=404)

    
