from django.contrib import admin
from .models import Graph, TemporaryFile

admin.site.register(Graph)
admin.site.register(TemporaryFile)