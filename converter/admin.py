from django.contrib import admin
from .models import Graph, TemporaryFile
from django.contrib.sessions.models import Session

admin.site.register(Graph)
admin.site.register(TemporaryFile)
admin.site.register(Session)