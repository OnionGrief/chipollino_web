import os

DJANGO_DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
DJANGO_DB = os.environ.get("DJANGO_DB")
CHIPOLLINO_BINARY = os.environ.get("CHIPOLLINO_BINARY", "build\\apps\\InterpreterApp\\Debug\\InterpreterApp.exe")
CHIPOLLINO_GENERATOR_BINARY = os.environ.get("CHIPOLLINO_GENERATOR_BINARY", "build\\apps\\InputGeneratorApp\\Debug\\InputGeneratorApp.exe")