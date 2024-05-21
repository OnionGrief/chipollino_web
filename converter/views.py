from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.generic import ListView, DetailView

def index(request):
    return render(request, 'converter/index.html')


from .chipollino_funcs import *

def generator(request):
    str1 = getString()
    return render(request, 'converter/generator.html', {'smth': str1})

from django.http import HttpResponse

def get_random_regex(request):
    return HttpResponse(getRegex())

    
