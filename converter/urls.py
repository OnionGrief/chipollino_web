from django.urls import path
from converter import views

app_name = 'converter'

urlpatterns = [
    path('', views.index, name='index'),
    path('generator/<slug:object_type>/', views.get_random_object, name='generator'),
    path('result/', views.run_interpreter, name='result'),
    path('get_pdf/', views.get_pdf, name='get_pdf'),
    path('tex_view/', views.tex_view, name='tex_view'),
    path('add_graph/', views.add_graph, name='add_graph'),
    path('delete_graphs/', views.delete_graphs, name='delete_graphs'),
    # path('delete_files/', views.delete_files, name='delete_files'),
]