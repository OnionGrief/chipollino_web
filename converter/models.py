from django.db import models
from django.core.files.storage import FileSystemStorage

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


class Graph(models.Model):
    nodes = models.JSONField(default=list)
    edges = models.JSONField(default=list)
    session_key = models.CharField(max_length=40)
    name = models.CharField(max_length=255, null=True)
    temporary_file = models.OneToOneField(TemporaryFile, on_delete=models.CASCADE, null=True)   
    def __str__(self):
        return self.name

