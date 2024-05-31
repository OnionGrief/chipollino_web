from django.db import models
from django.core.files.storage import FileSystemStorage
class TemporaryFile(models.Model):
    path = models.TextField(primary_key=True)
    created_at = models.DateTimeField(auto_now=True)


class Graph(models.Model):
    nodes = models.JSONField(default=list)
    edges = models.JSONField(default=list)
    name = models.CharField(max_length=255, null=True)

