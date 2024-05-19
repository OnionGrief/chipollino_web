import grpc

# Импорт протокола gRPC
from .generated import converter_pb2 as generated_pb2
from .generated import converter_pb2_grpc as generated_pb2_grpc

# Создайте канал gRPC
channel = grpc.insecure_channel('localhost:50051')

# Создайте заглушку gRPC
stub = generated_pb2_grpc.GreeterStub(channel)

# Создайте объект запроса
request = generated_pb2.StringRequest()
request.name = "Ваше имя"

# Вызовите метод gRPC по нажатию кнопки
def getString():
    response = stub.getString(request)
    return response.text