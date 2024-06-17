from django.db import models
from django.core.files.storage import FileSystemStorage
import json

# fs = FileSystemStorage(location='Chipollino/report.pdf')

# class File(models.Model):
#     file = models.FileField(storage=fs)

#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)
#         self.file.add_file(self.file.path)

class TemporaryFile(models.Model):
    path = models.TextField(primary_key=True)
    session_key = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.path


class GraphDB(models.Model):
    nodes = models.JSONField(default=list)
    edges = models.JSONField(default=list)
    session_key = models.CharField(max_length=40, null=True)
    name = models.CharField(max_length=255, null=True)
    TYPE_CHOICES = [
        ('NFA', 'NFA'),
        ('MFA', 'MFA')
    ]
    type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        default='NFA',
    )
    # temporary_file = models.OneToOneField(TemporaryFile, on_delete=models.CASCADE, null=True)   
    def __str__(self):
        return f'{self.name} {self.session_key}'
        return f'nodes: {self.nodes}\nedges:{self.edges}'
    def to_Graph(self):
        return Graph(id=self.id, nodes=json.loads(self.nodes), edges=json.loads(self.edges), name=self.name, type=self.type)

class Table:
    def __init__(self, columns, rows):
        self.columns = columns
        self.rows = rows

class Graph(): 
    def __init__(self, nodes, edges, name="", id=0, type="NFA"):
        self.nodes = nodes
        self.edges = edges
        self.name = name
        self.id = id
        self.type = type
    def to_GraphDB(self):
        return GraphDB(id=self.id, nodes=json.dumps(list(self.nodes)), edges=json.dumps(self.edges), name=self.name, type=self.type)

