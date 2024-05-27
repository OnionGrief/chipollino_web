from django.db import models

class Graph(models.Model):
    nodes = models.JSONField(default=list)
    edges = models.JSONField(default=list)
    name = models.CharField(max_length=255, null=True)

# Create your models here.
