from django.urls import path
from converter import views

app_name = 'converter'

urlpatterns = [
    path('', views.index, name='index'),
    # path('generator/', views.generator, name='generator'),
    path('getregex/', views.get_random_regex, name='getregex'),
    path('result/', views.run_interpreter, name='result'),
    path('pdf_view/', views.pdf_view, name='pdf_view'),
]