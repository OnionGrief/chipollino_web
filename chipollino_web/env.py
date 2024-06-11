import os

DJANGO_DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
DJANGO_DB = os.environ.get("DJANGO_DB")

CHIPOLLINO_BINARY = ""
CHIPOLLINO_GENERATOR_BINARY = ""
if os.name == "nt":
    CHIPOLLINO_BINARY = "build\\apps\\InterpreterApp\\Debug\\InterpreterApp.exe"
    CHIPOLLINO_GENERATOR_BINARY = "build\\apps\\InputGeneratorApp\\Debug\\InputGeneratorApp.exe"
if os.name == "posix":
    CHIPOLLINO_BINARY = "build/apps/InterpreterApp/InterpreterApp"
    CHIPOLLINO_GENERATOR_BINARY = "build/apps/InputGeneratorApp/InputGeneratorApp"
CHIPOLLINO_BINARY = os.environ.get("CHIPOLLINO_BINARY", CHIPOLLINO_BINARY)
CHIPOLLINO_GENERATOR_BINARY = os.environ.get("CHIPOLLINO_GENERATOR_BINARY", CHIPOLLINO_GENERATOR_BINARY)