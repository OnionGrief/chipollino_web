# import grpc
# from .generated import converter_pb2 as generated_pb2
# from .generated import converter_pb2_grpc as generated_pb2_grpc

# channel = grpc.insecure_channel('localhost:50051')
# stub = generated_pb2_grpc.GreeterStub(channel)

import os
import subprocess


def getString():
    # request = generated_pb2.StringRequest()
    # request.name = "web client"
    # response = stub.getString(request)
    # return response.text
    return "hello world"

def getRegex():
    # request = generated_pb2.RegexRequest()
    # response = stub.getRegex(request)
    # return response.result
    return "a*b(a|b)"

def getNFA():
    return """NFA
    q1 initial_state
    ...
    q1 q2 a"""



def run_interpreter(text):
    try:
        os.chdir('Chipollino')
        subprocess.run('build/apps/InterpreterApp/Debug/InterpreterApp.exe', check=True)
        os.chdir('../')
    except subprocess.CalledProcessError:
        os.chdir('../')
        return None
    with open("Chipollino/resources/report.tex", 'r', encoding='utf-8') as tex_file:
        return tex_file.read()