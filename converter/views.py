from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.generic import ListView, DetailView

def index(request):
    return render(request, 'converter/index.html')


from .grpc_client import getString

def generator(request):
    str1 = getString()
    return render(request, 'converter/generator.html', {'smth': str1})

    
