from django.contrib import admin
from .models import GraphDB, TemporaryFile
from django.contrib.sessions.models import Session

admin.site.register(GraphDB)
admin.site.register(TemporaryFile)
admin.site.register(Session)