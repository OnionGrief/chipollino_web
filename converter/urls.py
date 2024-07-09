from django.urls import path
from converter import views

app_name = 'converter'

urlpatterns = [
    path('', views.index, name='index'),
    path('generator/<slug:object_type>/', views.get_random_object, name='generator'),
    path('result/', views.run_interpreter, name='result'),
    path('get_pdf/', views.get_pdf, name='get_pdf'),
    path('tex_view/', views.tex_view, name='tex_view'),
    path('get_graph/<int:graph_id>/', views.get_graph, name='get_graph'),
    path('get_svg_graph/', views.get_svg_graph, name='get_svg_graph'),
    path('get_graph/<int:graph_id>/<slug:format_name>/', views.get_graph_format, name='get_graph_format'),
    path('convert_graph_format/<slug:format_name>/', views.convert_graph_format, name='convert_graph_format'),
    path('create_graph/', views.create_graph, name='create_graph'),
    path('add_graph/', views.add_graph, name='add_graph'),
    path('delete_graph/<int:graph_id>/', views.delete_graph, name='delete_graph'),
    path('save_graph/<int:graph_id>/', views.save_graph, name='save_graph'),
    path('delete_graphs/', views.delete_graphs, name='delete_graphs'),
    # path('delete_files/', views.delete_files, name='delete_files'),
    path('load_yaml_data/', views.load_yaml_data, name='load_yaml_data'),
    path('help/', views.help_page, name='help'),
]