from django.contrib import admin
from .models import GraphDB, TemporaryFile
from django.contrib.sessions.models import Session

@admin.register(GraphDB)
class GraphDBAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'session_key')
admin.site.register(TemporaryFile)
admin.site.register(Session)