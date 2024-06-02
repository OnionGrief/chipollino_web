from django.shortcuts import render
from django.http import HttpResponse
import os
from .models import TemporaryFile

def index(request):
    if not request.session.session_key:
        request.session.create()
    return render(request, 'converter/index.html')


from converter.src import chipollino_funcs

def run_interpreter(request):
    session_key = request.session.session_key
    if request.method == 'POST':
        text = request.POST['input-txt']
        running_res, ok = chipollino_funcs.run_interpreter(text, session_key)
        if ok:
            tex_file = running_res
            result_list = chipollino_funcs.parse_tex(tex_file, session_key = session_key)
            return render(request, 'converter/result.html', {'success': True, 'test': text, 'texresult': tex_file, 'result_list': result_list})
        else:
            if running_res:
                return render(request, 'converter/result.html', {'test': running_res})
            else:
                return render(request, 'converter/result.html', {'test': "Converter error"})

def pdf_view(request):
    pdf_file = chipollino_funcs.get_pdf(request.session.session_key)
    if pdf_file:
            return HttpResponse(pdf_file, content_type='application/pdf')
    else:
        return HttpResponse("PDF file not found", status=404)

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
    except Session.DoesNotExist:
        return False
    return False

def delete_files(request):
    old_files = TemporaryFile.objects.filter(created_at__lt = datetime.utcnow() - timedelta(days=1))
    count = 0
    for file in old_files:
        if not is_session_active(file.session_key):
            os.remove(file.path)
            file.delete()
            count += 1
    return HttpResponse(f"deleted {count} files")

    
