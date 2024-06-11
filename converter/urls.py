from django.urls import path
from converter import views

app_name = 'converter'

urlpatterns = [
    path('', views.index, name='index'),
    path('generator/<slug:object_type>/', views.get_random_object, name='generator'),
    path('result/', views.run_interpreter, name='result'),
    path('pdf_view/', views.pdf_view, name='pdf_view'),
    path('tikz_view/', views.tikz_view, name='tikz_view'),
    # path('delete_files/', views.delete_files, name='delete_files'),
]